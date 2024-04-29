from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from handlers.support import SupportClass
from utils.data_base import DataBase
from utils.verification_methods import VerifyingEmail
from utils.states import *


__all__ = [
    'RegistrationHandler'
]


class RegistrationHandler(SupportClass):

    def __init__(self):
        super().__init__()
        self._registration_kb()

    async def command_start(self, message: Message, state: FSMContext):
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

        else:
            await self.main_menu(message, state)

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
        data_check_res = await self._data_checker(message, message.text)

        if data_check_res[0]:
            user_years_is_18 = await self.is_adult(message, data_check_res[1])
            if user_years_is_18:
                await state.update_data(BIRTHDAY=message.text)

                state_data = await state.get_data()
                pool = await DataBase.get_pool()
                async with pool.acquire() as con:
                    await con.fetch(
                        """INSERT INTO users(id, first_name, second_name, birthday)
                    VALUES ($1, $2, $3, $4)""",
                        state_data['USER_ID'],
                        state_data['FIRST_NAME'],
                        state_data['SECOND_NAME'],
                        data_check_res[1]
                    )

                await message.answer(
                    "Зараз потрібно верифікувати свій email, \nви це можете зробити потом \nВведіть email",
                    reply_markup=self._skip_email
                )
                await state.set_state(RegistrationState.INPUT_EMAIL)

    async def set_email(self, message: Message, state: FSMContext):
        if message.text == "Пропустити ⤴️":
            await message.answer(
                """Ви завжди можете вказати свій email
але пока ви не можете орендувати кімнати""",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.main_menu(message, state)
            return None

        if await self._length_checker(message, 64):
            if await self.is_email(message.text):
                await state.update_data(EMAIL=message.text)
                await VerifyingEmail.send_message(message, state)
                await message.answer(
                    f"Вам на {message.text} має прийти код для верифікації \nВведіть його в поле нижче",
                    reply_markup=self._verification_email_kb1
                )
                await state.set_state(RegistrationState.VERIFICATION_EMAIL)

            else:
                await message.answer("Ви ввели не email")

    async def check_verification_email_key(self, message: Message, state: FSMContext):
        if message.text == 'Відправити ще раз 🔄':
            await VerifyingEmail.send_message(message, state)
            await message.answer(
                f"Вам на {message.text} має прийти код для верифікації \nВведіть його в поле нижче",
                reply_markup=self._verification_email_kb2
            )
            await state.set_state(RegistrationState.VERIFICATION_EMAIL)

        elif message.text == "Назад ⬅️":
            await message.answer(
                """Ви завжди можете вказати свій email
але пока ви не можете орендувати кімнати""",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.main_menu(message, state)

        elif message.text.isnumeric() and len(message.text) == 6:
            is_verified = await VerifyingEmail.check_verifying_key(message, state)
            if is_verified:
                await message.answer(
                    "Ваш email верифікований",
                    reply_markup=ReplyKeyboardRemove()
                )
                await self.main_menu(message, state)

        else:
            await message.answer("Ви ввели не код")
