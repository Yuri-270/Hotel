from dotenv import dotenv_values
from pydantic import BaseModel, SecretStr


__all__ = [
    'Settings'
]


class Settings(BaseModel):
    __bot_token: SecretStr
    __cryptography_key: SecretStr
    __email_addr = str
    __email_key: SecretStr
    __host: str
    __port: int
    __user: str
    __db_password: SecretStr
    __db_name: str

    def __new__(cls, *args, **kwargs):
        env_values = dotenv_values('datas/.env')
        env_keys = list(env_values.keys())

        cls.__bot_token = SecretStr(env_values[env_keys[0]])
        cls.__cryptography_key = SecretStr(env_values[env_keys[1]])
        cls.__email_addr = str(env_values[env_keys[2]])
        cls.__email_key = SecretStr(env_values[env_keys[3]])
        cls.__host = str(env_values[env_keys[4]])
        cls.__port = int(env_values[env_keys[5]])
        cls.__user = str(env_values[env_keys[6]])
        cls.__db_password = SecretStr(env_values[env_keys[7]])
        cls.__db_name = str(env_values[env_keys[8]])

    @classmethod
    async def get_bot_token(cls) -> str:
        return cls.__bot_token.get_secret_value()

    @classmethod
    async def get_cryptography_key(cls) -> str:
        return cls.__cryptography_key.get_secret_value()

    @classmethod
    async def get_gmail_data(cls) -> tuple:
        """:return tuple[gmail_addr, gmail_key]"""
        gmail_key = cls.__email_key.get_secret_value()  # Get secret key
        gmail_data = (
            cls.__email_addr,
            gmail_key.replace('_', ' ')
        )

        return gmail_data

    @classmethod
    async def get_db_data(cls) -> dict:
        db_datas = {
            "host": cls.__host,
            "port": cls.__port,
            "user": cls.__user,
            "password": cls.__db_password.get_secret_value(),
            "database_name": cls.__db_name
        }
        return db_datas
