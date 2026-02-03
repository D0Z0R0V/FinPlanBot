import asyncpg
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
        
async def list_expense(telegram_id: int):
    conn = await get_connect()
    
    try:
        rows = await conn.fetch(
            """SELECT r.id, r.total_sum, c.name AS category, r.record_date, r.comments
            FROM records r
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE r.telegram_id = $1  -- добавить фильтр по пользователю
            ORDER BY r.record_date DESC""",
            telegram_id
        )
        
        return [
            {
                "id": row["id"],
                "total_sum": row["total_sum"],
                "category": row["category"],
                "record_date": row["record_date"],
                "comments": row["comments"],
            }
            for row in rows
        ]
        
    finally:
        await conn.close()
        
async def add_expense(telegram_id: int, total_sum: float, category_id: int = None, comments: str = None):
    """Добавить расход"""
    conn = await get_connect()
    try:
        await conn.execute(
            "INSERT INTO records (telegram_id, total_sum, category_id, comments) VALUES ($1, $2, $3, $4)",
            telegram_id,
            total_sum,
            category_id,
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
        