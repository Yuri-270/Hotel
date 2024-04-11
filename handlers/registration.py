from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

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
                "Привіт 🖐 \nдля початку роботи введи своє ім'я",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(RegistrationState.INPUT_FIRST_NAME)

        else:  # TODO main menu
            ...

    async def set_first_name(self, message: Message, state: FSMContext):
        if await self._length_checker(message, 32):
            await state.update_data(FIRST_NAME=message.text)

            await message.answer("Введіть своє прізвище", reply_markup=ReplyKeyboardRemove())
            await state.set_state(RegistrationState.INPUT_SECOND_NAME)

    async def set_second_name(self, message: Message, state: FSMContext):
        if await self._length_checker(message, 32):
            await state.update_data(SECOND_NAME=message.text)

            await message.answer(
                "Введіть свою дату народження 📅 \nДата має бути в форматі <i>dd.mm.yyyy</i>",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode=ParseMode.HTML
            )
            await state.set_state(RegistrationState.INPUT_BIRTHDAY)

    async def set_birthday(self, message: Message, state: FSMContext):
        if await self._length_checker(message, 10):
            ...
