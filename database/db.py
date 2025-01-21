import asyncpg
from config import DB_CONFIG

async def init_db():
    """Инициализация базы данных из SQL-скрипта."""
    with open("database/init_db.sql", "r") as f:
        create_tables_query = f.read()

    conn = await asyncpg.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["dbname"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"]
    )
    try:
        await conn.execute(create_tables_query)
        print("База успешно инициализирована.")
    finally:
        await conn.close()
