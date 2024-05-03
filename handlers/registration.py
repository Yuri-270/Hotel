from datetime import datetime

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
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
        data_check_res = await self._date_checker(message, message.text)

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
                    reply_markup=self._verification_email_kb
                )
                await state.set_state(RegistrationState.VERIFICATION_EMAIL)

            else:
                await message.answer("Ви ввели не email")

    async def check_verification_email_key(self, message: Message, state: FSMContext):
        if message.text == 'Відправити ще раз 🔄':
            await VerifyingEmail.send_message(message, state)
            await message.answer(
                f"Вам на {message.text} має прийти код для верифікації \nВведіть його в поле нижче",
                reply_markup=self._back_kb
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
                    """Ваш email верифікований
Тепер потрібно щоб ви добавили свій номер телефону
Це можна зробити потім""",
                    reply_markup=self._skip_phone_number
                )
                await state.set_state(RegistrationState.INPUT_TELEPHONE_NUMBER)

        else:
            await message.answer("Ви ввели не код")

    async def set_telephone_number(self, message: Message, state: FSMContext):
        if message.text == "Пропустити ⤴️":
            await message.answer(
                "Ви можете потім ввести номер телефона \nале пока ви не можете орендувати кімнати",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.main_menu(message, state)

        else:
            phone_number = message.text
            if phone_number[0] == '+':
                phone_number = phone_number[1:-1]

            if phone_number.isnumeric():
                state_data = await state.get_data()
                pool = await DataBase.get_pool()
                async with pool.acquire() as con:
                    await con.fetch(
                        "UPDATE users SET telephone_number = $1 WHERE id = $2",
                        int(phone_number),
                        state_data['USER_ID']
                    )

                await message.answer(
                    "Номер телефона добавлений, тепер потрібно добавити дані паспорта",
                    reply_markup=ReplyKeyboardRemove()
                )
                await message.answer(
                    "Ви дозволяєте обробку своїх данних",
                    reply_markup=self._confirm_data_ikb
                )
                await state.set_state(RegistrationState.CONFIRM_THE_TRANSFER_PASSPORT_DATA)

    async def input_passport_number(self, call: CallbackQuery, state: FSMContext):
        if call.data == 'no':
            await call.message.answer(
                "Ви можете потом ввести дані паспорта \nале пока ви не можете орендувати кімнати",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.main_menu(call.message, state)

        elif call.data == 'yes':
            await call.message.answer(
                "Введіть номер паспорта",
                reply_markup=self._back_kb
            )
            await state.set_state(RegistrationState.INPUT_PASSPORT_NUMBER)

    async def get_passport_data(self, message: Message, state: FSMContext):
        if message.text == 'Назад ⬅️':
            await message.answer(
                "Ви можете потом ввести дані паспорта \nале пока ви не можете орендувати кімнати",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.main_menu(message, state)

        elif message.text.isnumeric() and len(message.text) == 9:
            state_data = await state.get_data()
            pool = await DataBase.get_pool()
            async with pool.acquire() as con:
                await con.fetch(
                    "UPDATE users SET passport_number = $1 WHERE id = $2",
                    message.text,
                    state_data['USER_ID']
                )
                await message.answer(
                    "Номер паспорта добавлений \nТепер введіть до якого він числа дійсний",
                    reply_markup=self._back_kb
                )
                await state.set_state(RegistrationState.INPUT_PASSPORT_VALID_UNTIL)

        else:
            await message.answer("Ви ввели не номер паспорта")

    async def get_passport_valid_until(self, message: Message, state: FSMContext):
        data_res = await self._date_checker(message, message.text)
        if message.text == 'Назад ⬅️':
            await message.answer(
                "Ви можете потом ввести дані паспорта \nале пока ви не можете орендувати кімнати",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.main_menu(message, state)

        elif data_res[0]:
            today_date = datetime.today()
            if today_date > data_res[1]:
                await message.answer("Паспорт прострочений!", reply_markup=self._back_kb)

            else:
                state_data = await state.get_data()
                pool = await DataBase.get_pool()
                async with pool.acquire() as con:
                    await con.fetch(
                        "UPDATE users SET passport_valid_until = $1 WHERE id = $2",
                        data_res[1],
                        state_data['USER_ID']
                    )

                await message.answer("Ви пройшли регістрацію \nТепер ви можете орендувати кімнати 🎉")
                await self.main_menu(message, state)

        else:
            await message.answer("Ви ввели не дату")
