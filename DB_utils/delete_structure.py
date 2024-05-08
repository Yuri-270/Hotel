from asyncio import run

from utils.data_base import DataBase
from config_reader import Settings


async def delete_structure():
    Settings()
    db_datas = await Settings.get_db_data()
    pool = await DataBase.create_pool(db_datas)
    async with pool.acquire() as con:
        try:
            await con.fetch("DROP TABLE hotels")
            await con.fetch("DROP TABLE rooms")
            await con.fetch("DROP TABLE additional_services")
            await con.fetch("DROP TABLE additional_services_in_hotel")
            await con.fetch("DROP TABLE users")
            await con.fetch("DROP TABLE booking")
            await con.fetch("DROP TABLE active_additional_services")

            await con.fetch("DROP SEQUENCE hotels_sequence")
            await con.fetch("DROP SEQUENCE rooms_sequence")
            await con.fetch("DROP SEQUENCE additional_service_sequence")
            await con.fetch("DROP SEQUENCE users_sequence")
            await con.fetch("DROP SEQUENCE booking_sequence")
            print(f'Структура видалена')
        except Exception as _ex:
            print(f'Ошибка: {_ex}')

if __name__ == '__main__':
    run(delete_structure())
