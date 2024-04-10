from asyncio import run
import logging
import sys

from aiogram import Bot, Dispatcher
import asyncpg

from utils.data_base import DataBase
from handlers.handler import router
from config import *


async def main():
    bot = Bot(TOKEN_API)
    dp = Dispatcher()
    dp.include_router(router)

    pool = await asyncpg.create_pool(
        host=db_data['host'],
        port=db_data['port'],
        user=db_data['user'],
        password=db_data['password'],
        database=db_data['database_name']
    )
    DataBase(pool)
    await DataBase.create_db()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        run(main())
    except KeyboardInterrupt:
        print('Bot is closed')
