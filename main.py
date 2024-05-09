from asyncio import run
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from utils.data_base import DataBase
from handlers.handler import router
from config_reader import *


__all__ = [
    'Settings'
]


Settings()


async def main():
    bot = Bot(await Settings.get_bot_token())
    dp = Dispatcher()
    dp.include_router(router)

    db_data: dict = await Settings.get_db_data()
    await DataBase.create_pool(db_data)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([BotCommand(command='start', description='Запуск бота')])
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        run(main())
    except KeyboardInterrupt:
        print('Bot is closed')
