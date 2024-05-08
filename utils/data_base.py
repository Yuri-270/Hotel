import asyncpg


__all__ = [
    'DataBase'
]


class DataBase:
    __pool: asyncpg.create_pool()

    def __new__(cls, pool):
        pass

    @classmethod
    async def create_pool(cls, db_data: dict) -> asyncpg.create_pool():
        pool = await asyncpg.create_pool(
            host=db_data['host'],
            port=db_data['port'],
            user=db_data['user'],
            password=db_data['password'],
            database=db_data['database_name']
        )
        cls.__pool = pool

        return cls.__pool

    @classmethod
    async def get_pool(cls) -> create_pool:
        return cls.__pool

    @classmethod
    async def create_structure(cls):
        async with cls.__pool.acquire() as con:

            # Create sequences
            await con.fetch("""CREATE SEQUENCE IF NOT EXISTS hotels_sequence""")
            await con.fetch("""CREATE SEQUENCE IF NOT EXISTS rooms_sequence""")
            await con.fetch("""CREATE SEQUENCE IF NOT EXISTS additional_service_sequence""")
            await con.fetch("""CREATE SEQUENCE IF NOT EXISTS users_sequence""")
            await con.fetch("""CREATE SEQUENCE IF NOT EXISTS booking_sequence""")

            # Create tables
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS hotels (
                    hotel_id INTEGER DEFAULT nextval ('hotels_sequence') PRIMARY KEY,
                    city VARCHAR(32) NOT NULL,
                    address VARCHAR(64) NOT NULL,
                    stars INTEGER NOT NULL,
                    num_of_rooms INTEGER NOT NULL
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER DEFAULT nextval ('rooms_sequence') PRIMARY KEY,
                    in_hotel INTEGER NOT NULL,
                    price_for_night REAL NOT NULL,
                    for_how_many_people INTEGER NOT NULL,
                    status VARCHAR(20) NOT NULL
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS additional_services (
                    id INTEGER DEFAULT nextval ('additional_service_sequence') PRIMARY KEY,
                    service_name VARCHAR(32) NOT NULL,
                    price REAL NOT NULL
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS additional_services_in_hotel (
                    hotel_id INTEGER NOT NULL,
                    service_id INTEGER NOT NULL
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS users (
                    id INTEGER DEFAULT nextval ('users_sequence') PRIMARY KEY,
                    first_name VARCHAR(32) NOT NULL,
                    second_name VARCHAR(32) NOT NULL,
                    birthday DATE NOT NULL,
                    email VARCHAR(48),
                    telephone_number BIGINT,
                    passport_number VARCHAR(32),
                    passport_valid_until DATE
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS booking (
                    booking_id INTEGER DEFAULT nextval ('booking_sequence') PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    date_of_arrival DATE NOT NULL,
                    num_of_nights INTEGER NOT NULL
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS active_additional_services (
                    service_id INTEGER NOT NULL,
                    booking_id INTEGER NOT NULL
                )"""
            )
