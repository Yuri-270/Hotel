from datetime import datetime
from re import match
import aiohttp

from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton as KeyBut
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton as InBut
from aiogram.fsm.context import FSMContext

from utils.states import MainState
from utils.data_base import DataBase


__all__ = [
    'SupportClass'
]


class SupportClass:
    _geo_ikb: ReplyKeyboardMarkup

    def __init__(self):
        self._back_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text="Назад ⬅️")]],
            resize_keyboard=True
        )
        self._confirm_data_ikb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InBut(text='Да 👍', callback_data='yes'),
                InBut(text='Нет 👎🏾', callback_data='no')
            ]]
        )

    def _registration_kb(self):
        self._skip_email = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text='Пропустити ⤴️')]],
            input_field_placeholder="name123@email.com",
            resize_keyboard=True
        )
        self._verification_email_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text='Відправити ще раз 🔄'), KeyBut(text="Назад ⬅️")]],
            resize_keyboard=True
        )

    @staticmethod
    async def get_phone_number_kb(skip_mode=True) -> ReplyKeyboardMarkup:
        text_button = "Пропустити ⤴️" if skip_mode else "Назад ⬅️"
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text=text_button)]],
            input_field_placeholder="+380",
            resize_keyboard=True
        )
        return kb

    @staticmethod
    async def _get_verification_email_kb(send_code_again=True) -> ReplyKeyboardMarkup:
        if send_code_again:
            buttons = [[KeyBut(text='Відправити ще раз 🔄'), KeyBut(text="Назад ⬅️")]]
        else:
            buttons = [[KeyBut(text="Назад ⬅️")]]

        ikb = ReplyKeyboardMarkup(
            keyboard=buttons,
            input_field_placeholder="Введіть 6-значний код сюда",
            resize_keyboard=True
        )
        return ikb

    def _rent_a_room_kb(self):
        # Get location
        self._geo_ikb = ReplyKeyboardMarkup(
            keyboard=[[
                KeyBut(text="Найти поруч 🗺", request_location=True),
                KeyBut(text="На головне меню ⤵️")
            ]],
            input_field_placeholder="Вкажіть місто",
            resize_keyboard=True
        )

        # Select hotel stars
        inline_buttons_for_stars = list()
        inline_row_for_stars = list()

        i = 1
        while i < 6:
            inline_row_for_stars.append(InBut(text=str(i), callback_data=str(i)))
            if len(inline_row_for_stars) == 2:
                inline_buttons_for_stars.append(inline_row_for_stars)
                inline_row_for_stars = []
            i += 1
        inline_buttons_for_stars.append([InBut(text='5', callback_data='5')])
        inline_buttons_for_stars.append([
            InBut(text="Пропустити", callback_data='anything'),
            InBut(text="На головне меню", callback_data='back')
        ])
        self._stars_ikb = InlineKeyboardMarkup(inline_keyboard=inline_buttons_for_stars)

        # Select starting price for night
        self._starting_price_for_night_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text="Від 0₴"), KeyBut(text="Назад ⤵️")]],
            resize_keyboard=True
        )

        # Select final price for night
        self._final_price_for_night_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text="До 100 000₴"), KeyBut(text="Назад ⤵️")]],
            resize_keyboard=True
        )

        # Select for how many people
        self._for_how_many_people_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyBut(text="Пропустити"), KeyBut(text="На головне меню ⤵️")]],
            resize_keyboard=True
        )

        # Do rent a room
        self._do_rent_a_room_ikb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InBut(text="Назад", callback_data='Back'),
                InBut(text="Орендувати", callback_data='Rent')
            ]]
        )

        # Today date
        self._set_date_of_arrival_kb = ReplyKeyboardMarkup(
            keyboard=[[
                KeyBut(text="Вказати сьогоднішню дату"),
                KeyBut(text="Назад ⤵️")
            ]],
            input_field_placeholder="Вкажіть дату в форматі dd.mm.yyyy",
            resize_keyboard=True
        )

        # Confirm payment ikb
        self._confirm_payment_ikb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InBut(text="Відмінити", callback_data='cancel'),
                InBut(text="Забронювати", callback_data='confirm')
            ]]
        )

    @staticmethod
    async def _rent_a_room_kb_builder(num_of_rooms: int) -> InlineKeyboardMarkup:
        i = 1
        buttons = list()
        button_row = list()
        while i <= num_of_rooms:
            button_row.append(InBut(text=str(i), callback_data=str(i)))
            if len(button_row) == 3:
                buttons.append(button_row)
                button_row = list()
            i += 1
        if len(button_row) != 0:
            buttons.append(button_row)

        buttons.append([
            InBut(text="Змінити місто", callback_data='Change_city'),
            InBut(text="На головне меню", callback_data='In_main_menu')
        ])

        ikb = InlineKeyboardMarkup(inline_keyboard=buttons)
        return ikb

    def _view_room_kbs(self):
        self._view_room_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InBut(text="Замовити доп послугу", callback_data="order_a_service")],
                [
                    InBut(text="Відмінити бронювання", callback_data="cancel_your_reservation"),
                    #InBut(text="Продлити бронювання", callback_data="extend_your_reservation")
                ],
                [InBut(text="На головне меню", callback_data="back")]
            ]
        )

    @staticmethod
    async def _get_service_kb(num_of_service: int) -> InlineKeyboardMarkup:
        service_row = list()
        i = 1
        while i <= num_of_service:
            service_row.append(InBut(text=str(i), callback_data=str(i)))
            i += 1

        buttons = [
            service_row,
            [InBut(text="На меню замовлення", callback_data="back")]
        ]

        ikb = InlineKeyboardMarkup(inline_keyboard=buttons)
        return ikb

    @staticmethod
    async def _user_cabinet_kb(
            have_email=True,
            have_phone_number=True,
            have_passport_data=True
    ) -> InlineKeyboardMarkup:
        buttons = list()
        first_row_buttons = list()

        # Button 'change email'
        button_data = "Змінити email" if have_email else "Добавити email"
        first_row_buttons.append(InBut(text=button_data, callback_data='change_email'))

        # Button 'change phone number'
        button_data = "Змінити номер телефону" if have_phone_number else "Добавити номер телефону"
        first_row_buttons.append(InBut(text=button_data, callback_data='change_number'))

        buttons.append(first_row_buttons)

        # Buttons 'add passport data'
        if have_passport_data is False:
            buttons.append([InBut(text="Добавити паспортні дані", callback_data='add_passport_data')])

        buttons.append([InBut(text="На головне меню", callback_data='in_main_menu')])

        ikb = InlineKeyboardMarkup(inline_keyboard=buttons)
        return ikb

    @classmethod
    async def delete_reply_kb(cls, message: Message, bot: Bot):
        message_data = await message.answer(
            "Delete kb",
            reply_markup=ReplyKeyboardRemove()
        )
        await bot.delete_message(chat_id=message_data.chat.id, message_id=message_data.message_id)

    @staticmethod
    async def main_menu_kb(user_id: int) -> ReplyKeyboardMarkup:
        buttons = [
            [KeyBut(text='Орендувати кімнату 🏙')],
            [KeyBut(text='Особистий кабінет 💼')]
        ]

        pool = await DataBase.get_pool()
        async with pool.acquire() as con:
            already_used = await con.fetchval(
                "SELECT COUNT(user_id) FROM booking WHERE user_id = $1 AND date_of_departure < CURRENT_DATE",
                user_id
            )

        if already_used != 0:
            buttons.insert(1, [KeyBut(text='Переглянути історію 🗓')])

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
    async def _date_checker(message: Message, data_for_checking: str):
        """Return tuple[True, date: datetime] if True;
        tuple [False, None] if False"""
        data_for_checking_arr = [i for i in data_for_checking]

        if len(data_for_checking_arr) >= 5:
            data_for_checking_arr[2] = '.'
            data_for_checking_arr[5] = '.'

        data_for_checking = ''
        for letter in data_for_checking_arr:
            data_for_checking += letter

        try:
            return True, datetime.strptime(data_for_checking, "%d.%m.%Y").date()
        except ValueError:
            await message.answer(
                "Дата не в форматі <i>dd.mm.yyyy</i>",
                parse_mode=ParseMode.HTML
            )
            return False, None

    @staticmethod
    async def is_adult(message: Message, selected_date):
        today_date = datetime.today().date()
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

    @staticmethod
    async def get_city_name(latitude: float, longitude: float) -> str:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                city = data.get('address', {}).get('city')
                if city is None:
                    city = data.get('address', {}).get('town')
                if city is None:
                    city = data.get('address', {}).get('village')
                if city is None:
                    city = data.get('address', {}).get('hamlet')
                if city is None:
                    city = data.get('address', {}).get('locality')
                return city
