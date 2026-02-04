import asyncio, os, logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import menu, gift, expense
from dotenv import load_dotenv
from config import BOT_TOKEN
from database.db import init_db

load_dotenv()

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_routers(
        menu.router,
        gift.router,
        expense.router
        
    )
    
    try:
        logging.info("Инициализация базы данных...")
        await init_db()
        logging.info("База успешно инициализирована!")
    except Exception as e:
        logging.error(f"Ошибка инициализации базы данных: {e}")
        return

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
