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
            await con.fetch(
                """CREATE SEQUENCE IF NOT EXISTS room_sequence
                START 1 INCREMENT 1"""
            )
            await con.fetch(
                """CREATE SEQUENCE IF NOT EXISTS personal_sequence
                START 1 INCREMENT 1"""
            )
            await con.fetch(
                """CREATE SEQUENCE IF NOT EXISTS booking_sequence
                START 1 INCREMENT 1"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS personal (
                    personal_id INTEGER DEFAULT nextval ('personal_sequence') PRIMARY KEY NOT NULL,
                    first_name CHAR(64) NOT NULL,
                    second_name CHAR(64) NOT NULL,
                    passport_data CHAR(32) NOT NULL,
                    post CHAR(32) NOT NULL
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS visitor (
                    visitor_id BIGINT PRIMARY KEY NOT NULL,
                    first_name CHAR(32) NOT NULL,
                    second_name CHAR(32) NOT NULL,
                    birthday DATE NOT NULL,
                    passport_data char(32) NOT NULL
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS room (
                    room_id INTEGER DEFAULT nextval('room_sequence') PRIMARY KEY NOT NULL,
                    num_of_people INT NOT NULL,
                    price_for_people REAL NOT NULL,
                    maid INT,
                    status CHAR(32) NOT NULL,
                    CONSTRAINT personal_fk FOREIGN KEY (maid) REFERENCES personal (personal_id)
                )"""
            )
            await con.fetch(
                """CREATE TABLE IF NOT EXISTS booking (
                    id INTEGER DEFAULT nextval ('booking_sequence') PRIMARY KEY NOT NULL,
                    user_id INT NOT NULL,
                    room_id INT NOT NULL,
                    date_of_entry DATE NOT NULL,
                    num_of_nights INT NOT NULL,
                    num_of_people INT NOT NULL,
                    CONSTRAINT user_fk FOREIGN KEY (user_id) REFERENCES visitor (visitor_id),
                    CONSTRAINT room_fk FOREIGN KEY (room_id) REFERENCES room (room_id)
                )"""
            )
