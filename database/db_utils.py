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

async def get_gift_list(user_id: int):
    conn = await get_connect()
    try:
        rows = await conn.fetch(
            "SELECT id, gift_name, comment, names FROM gift") #WHERE user_id = $1", user_id
        
        return [
            {"id": row["id"], "gift_name": row["gift_name"], "comment": row["comment"], "names": row["names"]}
            for row in rows
        ]
    finally:
        await conn.close()

async def add_gift(user_id: int, gift_name: str, comment: str, names: str):
    conn = await get_connect()
    try:
        await conn.execute(
            "INSERT INTO gift (user_id, gift_name, comment, names) VALUES ($1, $2, $3, $4)",
            user_id,
            gift_name,
            comment,
            names
        )
    finally:
        await conn.close()

async def delete_gift(gift_id: int, user_id: int):
    conn = await get_connect()
    try:
        result = await conn.execute(
            "DELETE FROM gift WHERE id = $1 AND user_id = $2", gift_id, user_id
        )

        if result == "DELETE 1":
            await conn.execute(
                "SELECT setval('gift_id_seq', COALESCE((SELECT MAX(id) FROM gift), 1), false);"
            )
            return True
        else:
            return False
    finally:
        await conn.close()
        
async def money_list():
    conn = await get_connect()
    
    try:
        rows = await conn.fetch(
            """SELECT r.id r.total_sum, c.name AS category, r.record_date, r.comments
            FROM records r
            LEFT JOIN categories c ON r.category_id = c.id
            ORDER BY r.record_date DESC"""
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
