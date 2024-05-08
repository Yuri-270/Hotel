from random import randint as rand, shuffle
import asyncio
import json

from utils.data_base import DataBase
from config_reader import Settings


async def add_datas():
    with open("datas/default_data.json", 'r', encoding='utf-8') as json_file:
        json_datas = json.load(json_file)

    Settings()
    db_datas = await Settings.get_db_data()
    pool = await DataBase.create_pool(db_datas)
    async with (pool.acquire() as con):

        def get_price_for_night(stars: int) -> int:
            start_price = 100 * stars
            final_price = start_price * 2
            return rand(start_price, final_price)

        # Create hotels
        i = 0
        while i < 164:
            await con.fetch(
                "INSERT INTO hotels (city, address, stars, num_of_rooms) VALUES ($1, $2, $3, $4)",
                json_datas['cities'][i][0],
                json_datas['cities'][i][1],
                json_datas['stars'][i],
                json_datas['rooms'][i]
            )
            i += 1
        print('Готелі створені')

        # Create rooms
        i1 = 0
        while i1 < 164:
            i2 = 0
            hotel_data = await con.fetchrow("SELECT * FROM hotels WHERE hotel_id = $1", i1 + 1)
            while i2 < hotel_data['num_of_rooms']:
                price_for_night = get_price_for_night(hotel_data['stars'])
                for_how_many_people = rand(1, 3)

                await con.fetch(
                    """INSERT INTO rooms (in_hotel, price_for_night, for_how_many_people, status)
                    VALUES ($1, $2, $3, $4)""",
                    hotel_data['hotel_id'],
                    price_for_night,
                    for_how_many_people,
                    'Ready to receive'
                )
                i2 += 1
            i1 += 1
        print('Кімнати створені')

        # Create services
        i = 0
        while i < 4:
            await con.fetch(
                """INSERT INTO additional_services(service_name, price) VALUES ($1, $2)""",
                json_datas['additional_services'][i][0],
                json_datas['additional_services'][i][1]
            )
            i += 1
        print('Доп услуги добавлені')

        # Connect services to hotel
        services = [i for i in range(1, 5)]
        i1 = 0
        while i1 < 164:
            i2 = 0
            num_of_services = rand(1, 4)
            shuffle(services)
            while i2 < num_of_services:
                await con.fetch(
                    "INSERT INTO additional_services_in_hotel VALUES($1, $2)",
                    i1+1,
                    services[i2]
                )
                i2 += 1
            i1 += 1
        print("До готелів прив'язані услуги")


if __name__ == '__main__':
    asyncio.run(add_datas())
