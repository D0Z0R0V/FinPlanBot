import asyncpg
from datetime import date, datetime
from config import DB_CONFIG

async def get_connect():
    return await asyncpg.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["dbname"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"]
    )

# ВАЖНО: параметр user_id - это на самом деле telegram_id!

async def get_gift_list(telegram_id: int):
    conn = await get_connect()
    try:
        rows = await conn.fetch(
            "SELECT id, gift_name, comment, names FROM gift WHERE telegram_id = $1", 
            telegram_id 
        )
        
        return [
            {"id": row["id"], "gift_name": row["gift_name"], "comment": row["comment"], "names": row["names"]}
            for row in rows
        ]
    finally:
        await conn.close()

async def add_gift(telegram_id: int, gift_name: str, comment: str, names: str):
    conn = await get_connect()
    try:
        await conn.execute(
            "INSERT INTO gift (telegram_id, gift_name, comment, names) VALUES ($1, $2, $3, $4)",  
            telegram_id,  
            gift_name,
            comment,
            names
        )
    finally:
        await conn.close()

async def delete_gift(gift_id: int, telegram_id: int):  
    conn = await get_connect()
    try:
        result = await conn.execute(
            "DELETE FROM gift WHERE id = $1 AND telegram_id = $2",  
            gift_id, 
            telegram_id  
        )

        if result == "DELETE 1":
            # Эта операция обычно не требуется, PostgreSQL сам управляет sequences
            await conn.execute(
                "SELECT setval('gift_id_seq', COALESCE((SELECT MAX(id) FROM gift), 1), false);"
            )
            return True
        else:
            return False
    finally:
        await conn.close()

async def get_income_list(telegram_id: int):
    conn = await get_connect()
    try:
        rows = await conn.fetch(
            """SELECT id, amount, source, record_date, comments 
            FROM income 
            WHERE telegram_id = $1
            ORDER BY record_date DESC""",
            telegram_id
        )
        
        return [
            {
                "id": row["id"],
                "amount": row["amount"],
                "source": row["source"],
                "record_date": row["record_date"],
                "comments": row["comments"],
            }
            for row in rows
        ]
    finally:
        await conn.close()

async def add_income(telegram_id: int, amount: float, source: str = None, comments: str = None):
    """Добавить доход"""
    conn = await get_connect()
    try:
        await conn.execute(
            "INSERT INTO income (telegram_id, amount, source, comments) VALUES ($1, $2, $3, $4)",
            telegram_id,
            amount,
            source,
            comments
        )
    finally:
        await conn.close()
        
async def delete_income(income_id: int, telegram_id: int):
    """Удалить доход"""
    conn = await get_connect()
    try:
        result = await conn.execute(
            "DELETE FROM income WHERE id = $1 AND telegram_id = $2",
            income_id,
            telegram_id
        )
        return result == "DELETE 1"
    finally:
        await conn.close()
        
        
async def add_expense(telegram_id: int, total_sum: float, category_name: str, comments: str = None):
    """Добавить расход"""
    conn = await get_connect()
    try:
        await conn.execute(
            "INSERT INTO records (telegram_id, total_sum, category_name, comments) VALUES ($1, $2, $3, $4)",
            telegram_id,
            total_sum,
            category_name,
            comments
        )
    finally:
        await conn.close()

async def delete_expense(expense_id: int, telegram_id: int):
    """Удалить расход"""
    conn = await get_connect()
    try:
        result = await conn.execute(
            "DELETE FROM records WHERE id = $1 AND telegram_id = $2",
            expense_id,
            telegram_id
        )
        return result == "DELETE 1"
    finally:
        await conn.close()
        
async def get_expense_list(telegram_id: int, limit: int = 20):
    """Получить список расходов пользователя"""
    conn = await get_connect()
    try:
        rows = await conn.fetch(
            """SELECT id, total_sum, category_name, record_date, comments 
            FROM records 
            WHERE telegram_id = $1
            ORDER BY record_date DESC, id DESC
            LIMIT $2""",
            telegram_id,
            limit
        )
        
        return [
            {
                "id": row["id"],
                "total_sum": row["total_sum"],
                "category_name": row["category_name"],
                "record_date": row["record_date"],
                "comments": row["comments"],
            }
            for row in rows
        ]
    finally:
        await conn.close()
        
        
async def register_user(telegram_id: int, name: str, role: str = "user"):
    """Зарегистрировать нового пользователя"""
    conn = await get_connect()
    try:
        # Пытаемся вставить пользователя, если он уже существует - игнорируем
        await conn.execute(
            """INSERT INTO users (telegram_id, name, role) 
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO UPDATE SET
            name = EXCLUDED.name,
            role = EXCLUDED.role""",
            telegram_id,
            name,
            role
        )
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        return False
    finally:
        await conn.close()

#Отчеты


async def get_financial_report_simple(telegram_id: int, start_date, end_date):
    """
    Упрощенный финансовый отчет за период
    Поддерживает как строки 'YYYY-MM-DD', так и объекты datetime.date
    """
    # Преобразуем в объекты date, если переданы строки
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Проверяем, что это действительно объекты date
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        raise TypeError("start_date и end_date должны быть строками 'YYYY-MM-DD' или объектами datetime.date")
    
    conn = await get_connect()
    try:
        # 1. Общая сумма доходов за период
        total_income = await conn.fetchval(
            """SELECT COALESCE(SUM(amount), 0) 
            FROM income 
            WHERE telegram_id = $1 
            AND record_date::date BETWEEN $2::date AND $3::date""",
            telegram_id, start_date, end_date
        )
        
        # 2. Общая сумма расходов за период
        total_expense = await conn.fetchval(
            """SELECT COALESCE(SUM(total_sum), 0) 
            FROM records 
            WHERE telegram_id = $1 
            AND record_date::date BETWEEN $2::date AND $3::date""",
            telegram_id, start_date, end_date
        )
        
        # 3. Расходы по категориям
        category_expenses = await conn.fetch(
            """SELECT 
                category_name,
                COALESCE(SUM(total_sum), 0) as total,
                COUNT(id) as count
            FROM records 
            WHERE telegram_id = $1 
            AND record_date::date BETWEEN $2::date AND $3::date
            GROUP BY category_name
            ORDER BY total DESC""",
            telegram_id, start_date, end_date
        )
        
        # Преобразуем обратно в строки для возвращаемого значения
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        return {
            "period": {"start": start_date_str, "end": end_date_str},
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(total_income - total_expense),
            "category_expenses": [
                {"category": row["category_name"], "total": float(row["total"]), "count": row["count"]}
                for row in category_expenses
            ]
        }
        
    finally:
        await conn.close()