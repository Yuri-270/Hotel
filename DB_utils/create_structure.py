from asyncio import run

from utils.data_base import DataBase
from config_reader import Settings


async def create_structure():
    Settings()
    db_data: dict = await Settings.get_db_data()
    await DataBase.create_pool(db_data)
    await DataBase.create_structure()


if __name__ == '__main__':
    run(create_structure())
