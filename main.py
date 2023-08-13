import os
import asyncio
from handlers import register_handlers
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import utils.database as db


async def main() -> None:
    load_dotenv('.env')
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=os.getenv('TOKEN'))
    register_handlers(dp)
    await db.db_start()
    await dp.start_polling(bot)
    await asyncio.sleep(0)


if __name__ == '__main__':
    asyncio.run(main())
