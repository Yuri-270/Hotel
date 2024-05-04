import json
import asyncio

from tqdm import tqdm
import asyncpg

from utils.data_base import DataBase
from config_reader import Settings


# Put "1" for take action
CREATE_DB = 0
DELETE_DB_DATA = 0
ADD_DATA_TO_DB = 0


async def connect_to_db():
    Settings()
    db_data: dict = await Settings.get_db_data()
    pool = await asyncpg.create_pool(
        host=db_data['host'],
        port=db_data['port'],
        user=db_data['user'],
        password=db_data['password'],
        database=db_data['database_name']
    )
    DataBase(pool)


async def get_json() -> dict:
    with open("datas/default_data.json", 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


async def add_data(json_datas: dict):
    pool = await DataBase.get_pool()
    async with pool.acquire() as con:
        i = 0
        while i < 164:
            await con.fetch(
                "INSERT INTO hotel (num_of_rooms, city, stars, address) VALUES ($1, $2, $3, $4)",
                json_datas['rooms'][i],
                json_datas['cities'][i][0],
                json_datas['stars'][i],
                json_datas['cities'][i][1]
            )
            i += 1


async def reset_sequence():
    pool = await DataBase.get_pool()
    async with pool.acquire() as con:
        await con.fetch("SELECT setval('hotel_sequence', 1, false)")
        await con.fetch("SELECT setval('room_sequence', 1, false)")
        await con.fetch("SELECT setval('personal_sequence', 1, false)")
        await con.fetch("SELECT setval('booking_sequence', 1, false)")


async def delete_datas_from_db():
    pool = await DataBase.get_pool()
    async with pool.acquire() as con:
        await con.fetch("DROP TABLE IF EXISTS hotel CASCADE")
        await con.fetch("DROP TABLE IF EXISTS room CASCADE")
        await con.fetch("DROP TABLE IF EXISTS additional_services CASCADE")
        await con.fetch("DROP TABLE IF EXISTS users CASCADE")
        await con.fetch("DROP TABLE IF EXISTS booking CASCADE")
        await con.fetch("DROP TABLE IF EXISTS active_additional_services CASCADE")
        await con.fetch("DROP SEQUENCE IF EXISTS hotel_sequence CASCADE")
        await con.fetch("DROP SEQUENCE IF EXISTS room_sequence CASCADE")
        await con.fetch("DROP SEQUENCE IF EXISTS personal_sequence CASCADE")
        await con.fetch("DROP SEQUENCE IF EXISTS booking_sequence CASCADE")


async def main():
    num_of_iteration = 1
    if CREATE_DB:
        num_of_iteration += 1
    if ADD_DATA_TO_DB:
        num_of_iteration += 1
    if DELETE_DB_DATA:
        num_of_iteration += 1

    progress_bar = tqdm(total=num_of_iteration)

    await connect_to_db()
    progress_bar.update(1)
    if CREATE_DB:
        await DataBase.create_db()
        progress_bar.update(1)

    if DELETE_DB_DATA:
        await delete_datas_from_db()
        progress_bar.update(1)

    if ADD_DATA_TO_DB:
        data = await get_json()
        await reset_sequence()
        await add_data(data)
        progress_bar.update(1)

    print('Сделано')


if __name__ == "__main__":
    asyncio.run(main())
