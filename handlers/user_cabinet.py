from datetime import datetime

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
            last_message = await message.answer(
                user_message,
                reply_markup=ikb,
                parse_mode=ParseMode.HTML
            )
            await state.update_data(LAST_MESSAGE=last_message)
            await state.set_state(UserCabinetState.USER_CABINET_HANDLER)

    async def user_cabinet_handler(self, call: CallbackQuery, state: FSMContext, bot: Bot):
        state_data = await state.update_data()
        last_message: call.Message = state_data['LAST_MESSAGE']
        await bot.delete_message(chat_id=last_message.chat.id, message_id=last_message.message_id)

        if call.data == "change_email":
            await call.message.answer(
                "Введіть ваш email",
                reply_markup=self._back_kb
            )
            await state.set_state(UserCabinetState.INPUT_EMAIL)

        elif call.data == "change_number":
            kb = await self.get_phone_number_kb(False)
            await call.message.answer(
                "Введіть номер телефону",
                reply_markup=kb
            )
            await state.set_state(UserCabinetState.INPUT_PHONE_NUMBER)

        elif call.data == "add_passport_data":
            await self.add_passport_data(call.message, state)

        elif call.data == "in_main_menu":
            await self.main_menu(call.message, state)

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

    async def set_new_phone_number(self, message: Message, state: FSMContext, bot: Bot):
        if message.text != "Назад ⬅️":
            phone_number = message.text
            if phone_number[0] == '+':
                phone_number = phone_number[1:-1]

            if phone_number.isnumeric() and len(phone_number) <= 12:
                pool = await DataBase.get_pool()
                async with pool.acquire() as con:
                    state_data = await state.get_data()
                    number_data = await con.fetchval(
                        "SELECT telephone_number FROM users WHERE id = $1",
                        state_data['USER_ID']
                    )
                    await con.fetch(
                        "UPDATE users SET telephone_number = $1 WHERE id = $2",
                        int(phone_number),
                        state_data['USER_ID']
                    )

                if number_data is None:
                    await message.answer("Номер добавлений")
                else:
                    await message.answer("Номер змінений")

        await self.user_cabinet(message, state, bot)

    async def add_passport_data(self, message: Message, state: FSMContext):
        last_message = await message.answer(
            "Ви дозволяєте обробку своїх данних",
            reply_markup=self._confirm_data_ikb
        )
        await state.update_data(LAST_MESSAGE=last_message)
        await state.set_state(UserCabinetState.CONFIRM_PASSPORT_DATA)

    async def passport_number_menu(self, call: CallbackQuery, state: FSMContext, bot: Bot):
        state_data = await state.get_data()
        last_message = state_data['LAST_MESSAGE']
        await bot.delete_message(chat_id=last_message.chat.id, message_id=last_message.message_id)

        if call.data == "yes":
            await call.message.answer(
                "Введіть номер паспорта",
                reply_markup=self._back_kb
            )
            await state.set_state(UserCabinetState.SET_PASSPORT_NUMBER)

        elif call.data == "no":
            await self.user_cabinet(call.message, state, bot)

    async def passport_valid_until_menu(self, message: Message, state: FSMContext, bot: Bot):
        if message.text == 'Назад ⬅️':
            await self.user_cabinet(message, state, bot)

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
                await state.set_state(UserCabinetState.SET_PASSPORT_VALID_UNTIL)

        else:
            await message.answer("Ви ввели не номер паспорта")

    async def set_passport_valid_until(self, message: Message, state: FSMContext, bot: Bot):
        if message.text == 'Назад ⬅️':
            await self.user_cabinet(message, state, bot)
            return None

        data_res = await self._date_checker(message, message.text)
        if data_res[0]:
            today_date = datetime.today().date()
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

                await message.answer("Паспортні дані добавлені 🎉")
                await self.user_cabinet(message, state, bot)
