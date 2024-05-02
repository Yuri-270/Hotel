from asyncpg import create_pool


__all__ = [
    'DataBase'
]


class DataBase:
    __pool: create_pool()

    def __new__(cls, pool):
        cls.__pool = pool

    @classmethod
    async def get_pool(cls) -> create_pool():
        return cls.__pool

    @classmethod
    async def create_db(cls):
        async with cls.__pool.acquire() as con:
            # Create sequence
            await con.fetch(
                """CREATE SEQUENCE IF NOT EXISTS hotel_sequence
                START WITH 1 
                INCREMENT BY 1
                MAXVALUE 100000000
                MINVALUE 1"""
            )
            await con.fetch(
                """CREATE SEQUENCE IF NOT EXISTS room_sequence
                START WITH 1 
                INCREMENT BY 1
                MAXVALUE 100000000
                MINVALUE 1"""
            )
            await con.fetch(
                """CREATE SEQUENCE IF NOT EXISTS personal_sequence
                START WITH 1 
                INCREMENT BY 1
                MAXVALUE 100000000
                MINVALUE 1"""
            )
            await con.fetch(
                """CREATE SEQUENCE IF NOT EXISTS booking_sequence
                START WITH 1 
                INCREMENT BY 1
                MAXVALUE 100000000
                MINVALUE 1"""
            )

            # Create table
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS hotel (
                    id INTEGER DEFAULT nextval ('hotel_sequence') PRIMARY KEY NOT NULL,
                    city VARCHAR(32) NOT NULL,
                    address TEXT NOT NULL,
                    stars INTEGER NOT NULL,
                    num_of_rooms INTEGER NOT NULL
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS additional_services (
                    id INTEGER PRIMARY KEY NOT NULL,
                    service_name VARCHAR(32) NOT NULL,
                    price REAL NOT NULL,
                    CONSTRAINT services_fk FOREIGN KEY (id) REFERENCES hotel (id)
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS room (
                    id INTEGER DEFAULT nextval('room_sequence') PRIMARY KEY NOT NULL,
                    in_hotel INTEGER NOT NULL,
                    price_for_night REAL NOT NULL,
                    for_how_many_people INT NOT NULL,
                    status VARCHAR(32) NOT NULL,
                    CONSTRAINT hotel_fk FOREIGN KEY (in_hotel) REFERENCES hotel (id)
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY NOT NULL,
                    first_name VARCHAR(64) NOT NULL,
                    second_name VARCHAR(64) NOT NULL,
                    birthday DATE NOT NULL,
                    email VARCHAR(48),
                    telephone_number INTEGER,
                    user_address VARCHAR(32),
                    passport_number VARCHAR(32),
                    passport_valid_until DATE
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS booking (
                    id INTEGER DEFAULT nextval ('booking_sequence') PRIMARY KEY NOT NULL,
                    user_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    date_of_arrival DATE NOT NULL,
                    num_of_nights INT NOT NULL,
                    CONSTRAINT user_fk FOREIGN KEY (user_id) REFERENCES users (id),
                    CONSTRAINT room_fk FOREIGN KEY (room_id) REFERENCES room (id)
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS active_additional_services(
                    id INTEGER,
                    booking_id INTEGER,
                    CONSTRAINT active_services_fk FOREIGN KEY (booking_id) REFERENCES booking (id)
                )"""
            )
