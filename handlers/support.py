from datetime import datetime

from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode


__all__ = [
    'SupportClass'
]


class SupportClass:

    def __init__(self):
        pass
        self._main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyBut(text='Орендувати кімнату 🏙')],
                [KeyBut(text='Настройки ⚙️')],
                [KeyBut(text='Особистий кабінет 💼')]
            ],
            resize_keyboard=True
        )

    async def main_menu(self, message: Message, state: FSMContext):
        await message.answer(
            "Главное меню 🏢",
            reply_markup=self._main_kb
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
