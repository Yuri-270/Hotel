from datetime import datetime
from re import match

from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton as KeyBut
from aiogram.fsm.context import FSMContext

from utils.states import MainState
from utils.data_base import DataBase


__all__ = [
    'SupportClass'
]


class SupportClass:

    def __init__(self):
        pass

    def _registration_kb(self):
        self._skip_email = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text='Пропустити ⤴️')]],
            resize_keyboard=True
        )
        self._verification_email_kb1 = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text='Відправити ще раз 🔄'), KeyBut(text="Назад ⬅️")]],
            resize_keyboard=True
        )
        self._verification_email_kb2 = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text="Назад ⬅️")]],
            resize_keyboard=True
        )

    @staticmethod
    async def main_menu_kb(user_id: int) -> ReplyKeyboardMarkup:
        buttons = [
            [KeyBut(text='Орендувати кімнату 🏙')],
            [KeyBut(text='Настройки ⚙️'), KeyBut(text='Особистий кабінет 💼')]
        ]

        pool = await DataBase.get_pool()
        async with pool.acquire() as con:
            already_used = await con.fetchval("SELECT COUNT(user_id) FROM booking WHERE user_id = $1", user_id)

        if already_used != 0:
            buttons.insert(1, [KeyBut(text='Переглянути історію')])

        kb = ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

        return kb

    async def main_menu(self, message: Message, state: FSMContext):
        # Get main kb
        state_data = await state.get_data()
        kb = await self.main_menu_kb(state_data['USER_ID'])

        await message.answer(
            "Главное меню 🏢",
            reply_markup=kb
        )
        await state.set_state(MainState.MAIN_HANDLER)

    @staticmethod
    async def _length_checker(message: Message, length_of_message: int) -> bool:
        if len(message.text) <= length_of_message:
            return True

        else:
            last_word = 'символів'
            if length_of_message % 10 == 1:
                last_word = 'символа'

            await message.answer(f"Повідомлення має містити менше {length_of_message} {last_word}")

            return False

    @staticmethod
    async def _data_checker(message: Message, data_for_checking: str):
        data_for_checking_arr = [i for i in data_for_checking]

        if len(data_for_checking_arr) >= 5:
            data_for_checking_arr[2] = '.'
            data_for_checking_arr[5] = '.'

        data_for_checking = ''
        for letter in data_for_checking_arr:
            data_for_checking += letter

        try:
            return True, datetime.strptime(data_for_checking, "%d.%m.%Y")
        except ValueError:
            await message.answer(
                "Дата не в форматі <i>dd.mm.yyyy</i>",
                parse_mode=ParseMode.HTML
            )
            return False, None

    @staticmethod
    async def is_adult(message: Message, selected_date):
        today_date = datetime.today()
        birth_date_ = today_date - selected_date

        if birth_date_.days // 365.25 >= 18:
            return True
        else:
            await message.answer("Вам немає 18 років")
            return False

    @staticmethod
    async def is_email(email: str) -> str:
        pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
        return match(pattern, email) is not None
