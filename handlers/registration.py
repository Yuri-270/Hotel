from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from handlers.support import SupportClass
from utils.data_base import DataBase
from utils.states import *


__all__ = [
    'RegistrationHandler'
]


class RegistrationHandler(SupportClass):

    def __init__(self):
        super().__init__()

    @staticmethod
    async def command_start(message: Message, state: FSMContext):
        await state.update_data(USER_ID=message.from_user.id)
        pool = await DataBase.get_pool()

        async with pool.acquire() as con:
            user_data = await con.fetchval(
                "SELECT id FROM users WHERE id = $1",
                message.from_user.id
            )

        if user_data is None:
            await message.answer(
                "Привет 🖐 \nдля початку роботи введи своє ім'я",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(RegistrationState.INPUT_FIRST_NAME)

        else:  # TODO main menu
            ...

    async def set_first_name(self, message: Message, state: FSMContext):
        if await self._length_checker(message, 32):
            await state.update_data(USERNAME=message.text)

            await message.answer("Тепер введіть своє прізвище", reply_markup=ReplyKeyboardRemove())
            await state.set_state(RegistrationState.INPUT_SECOND_NAME)
