from asyncio import run

from utils.data_base import DataBase
from config_reader import Settings


async def delete_datas():
    Settings()
    db_datas = await Settings.get_db_data()
    pool = await DataBase.create_pool(db_datas)
    async with pool.acquire() as con:
        try:
            # Clear table
            await con.fetch("DELETE FROM hotels")
            await con.fetch("DELETE FROM rooms")
            await con.fetch("DELETE FROM additional_services")
            await con.fetch("DELETE FROM additional_services_in_hotel")
            await con.fetch("DELETE FROM users")
            await con.fetch("DELETE FROM booking")
            await con.fetch("DELETE FROM active_additional_services")

            # Reset sequence
            await con.fetch("SELECT setval('hotels_sequence', 1)")
            await con.fetch("SELECT setval('rooms_sequence', 1)")
            await con.fetch("SELECT setval('additional_service_sequence', 1)")
            await con.fetch("SELECT setval('users_sequence', 1)")
            await con.fetch("SELECT setval('booking_sequence', 1)")
            print("Дані видалені та послідовності скинуті")

        except Exception as _ex:
            print(f'Ошибка: {_ex}')

if __name__ == '__main__':
    run(delete_datas())
