from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from handlers.support import SupportClass
from utils.states import UserCabinetState
from utils.verification_methods import VerifyingEmail
from utils.data_base import DataBase


__all__ = [
    "UserCabinet"
]


class UserCabinet(SupportClass):

    def __init__(self):
        super().__init__()

    async def user_cabinet(self, message: Message, state: FSMContext, bot: Bot):
        await self.delete_reply_kb(message, bot)

        pool = await DataBase.get_pool()
        async with pool.acquire() as con:
            state_data = await state.get_data()
            user_data = await con.fetchrow(
                """SELECT first_name, second_name, birthday, email, 
                telephone_number, passport_number, passport_valid_until
                FROM users WHERE id = $1""",
                state_data['USER_ID']
            )

            user_message = f"""Особистий кабінет 💼

Ім'я: <i>{user_data['first_name']}</i>
Прізвище: <i>{user_data['second_name']}</i>
День народження: <b><i>{user_data['birthday']}</i></b>

Контакти
Email: """

            # Check email
            if user_data['email'] is None:
                user_message += "<b>Не указаний</b>"
                have_email = False
            else:
                user_message += f"{user_data['email']}"
                have_email = True

            # Check phone number
            user_message += "\nНомер телефона: "
            if user_data['telephone_number'] is None:
                user_message += "<b>Не указаний</b>"
                have_phone_number = False
            else:
                user_message += f"{user_data['telephone_number']}"
                have_phone_number = True

            # Check passport data
            user_message += "\nПаспортні дані "
            if user_data['passport_number'] is None or user_data['passport_valid_until'] is None:
                user_message += "не добавлені ❌"
                have_passport_data = False
            else:
                user_message += "добавлені ✅"
                have_passport_data = True

            ikb = await self._user_cabinet_kb(have_email, have_phone_number, have_passport_data)
            await message.answer(
                user_message,
                reply_markup=ikb,
                parse_mode=ParseMode.HTML
            )
            await state.set_state(UserCabinetState.USER_CABINET_HANDLER)

    async def user_cabinet_handler(self, call: CallbackQuery, state: FSMContext):
        if call.data == "change_email":
            await call.message.answer(
                "Введіть ваш email",
                reply_markup=self._back_kb
            )
            await state.set_state(UserCabinetState.INPUT_EMAIL)

        elif call.data == "change_number":
            pass
        elif call.data == "add_passport_data":
            pass
        elif call.data == "in_main_menu":
            pass

    async def set_email(self, message: Message, state: FSMContext, bot: Bot):
        if message.text == "Назад ⬅️":
            await self.user_cabinet(message, state, bot)

        elif await self.is_email(message.text):
            await state.update_data(EMAIL=message.text)
            await VerifyingEmail.send_message(message, state)
            kb = await self._get_verification_email_kb()
            await message.answer(
                f"Вам на {message.text} має прийти код для верифікації \nВведіть його в поле нижче",
                reply_markup=kb
            )
            await state.set_state(UserCabinetState.CONFIRM_EMAIL)

        else:
            await message.answer("Ви ввели не email")

    async def confirm_email(self, message: Message, state: FSMContext, bot: Bot):
        state_data = await state.get_data()
        pool = await DataBase.get_pool()
        async with pool.acquire() as con:
            used_to_be_email = await con.fetchval(
                "SELECT email FROM users WHERE id = $1",
                state_data['USER_ID']
            )

            if message.text == "Відправити ще раз 🔄":
                await VerifyingEmail.send_message(message, state)
                kb = await self._get_verification_email_kb(False)
                state_data = await state.get_data()
                await message.answer(
                    f"Вам на {state_data['EMAIL']} має прийти код для верифікації \nВведіть його в поле нижче",
                    reply_markup=kb
                )
                await state.set_state(UserCabinetState.CONFIRM_EMAIL)

            elif message.text == "Назад ⬅️":
                await self.user_cabinet(message, state, bot)

            elif await VerifyingEmail.check_verifying_key(message, state):
                await con.fetch(
                    "UPDATE users SET email = $1 WHERE id = $2",
                    state_data['EMAIL'],
                    state_data['USER_ID']
                )

            if used_to_be_email is None:
                await message.answer("Email добавлений")
            else:
                await message.answer("Email змінений")

            await self.user_cabinet(message, state, bot)
