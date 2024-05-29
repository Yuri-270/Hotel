from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from handlers.support import SupportClass
from handlers.rent_a_room import RentARoom
from utils.states import SelectHotel, UserCabinet
from utils.data_base import DataBase


__all__ = [
    'MainHandler'
]


class MainHandler(SupportClass):
    rent_a_room_class = RentARoom()

    def __init__(self):
        super().__init__()
        self._rent_a_room_kb()

    async def main_handler(self, message: Message, state: FSMContext):
        match message.text:

            case 'Орендувати кімнату 🏙':
                await self.rent_a_room(message, state)

            case 'Переглянути історію 🗓':
                await self.check_history(message, state)

            case 'Особистий кабінет 💼':
                await self.user_cabinet(message, state)

            case _:
                await message.answer("Виберіть з меню ⬇️")

    async def rent_a_room(self, message: Message, state: FSMContext):
        await self.__check_authorization_data(message, state)
        state_data = await state.get_data()
        if state_data['CITY'] is None:
            await message.answer(
                "Виберіть місто",
                reply_markup=self._geo_ikb
            )
            await state.set_state(SelectHotel.GET_LOCATION)

        else:
            await self.rent_a_room_class.get_hotels(message, state)

    @staticmethod
    async def __check_authorization_data(message: Message, state: FSMContext) -> bool:
        state_data = await state.get_data()
        pool = await DataBase.get_pool()
        async with pool.acquire() as con:
            users_data = await con.fetchrow(
                "SELECT email, telephone_number, passport_number, passport_valid_until FROM users WHERE id = $1",
                state_data['USER_ID']
            )

            all_data_confirm = True
            if users_data['email'] is None:
                all_data_confirm = False
            elif users_data['telephone_number']:
                all_data_confirm = False
            elif users_data['passport_number']:
                all_data_confirm = False
            elif users_data['passport_valid_until']:
                all_data_confirm = False

            if all_data_confirm is False:
                await message.answer("""Ви не вказали всі дані щоб бронювати кімнати
Пока що ви можете тише їх лише переглядати""")

        return all_data_confirm

    async def set_location(self, message: Message, state: FSMContext):
        if message.location:
            user_city = await self.get_city_name(
                message.location.latitude,
                message.location.longitude
            )
            await message.answer(f"Вибрано місто <b>{user_city.capitalize()}</b>", parse_mode='HTML')
            await state.update_data(CITY=user_city.capitalize())
            await self.rent_a_room(message, state)

        elif message.text == "На головне меню ⤵️":
            await self.main_menu(message, state)

        else:
            await message.answer(f"Вибрано місто <b>{message.text.capitalize()}</b>", parse_mode='HTML')
            await state.update_data(CITY=message.text.capitalize())
            await self.rent_a_room(message, state)

    async def user_cabinet(self, message: Message, state: FSMContext):
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
            await state.set_state(UserCabinet.USER_CABINET_HANDLER)

    async def check_history(self, message: Message, state: FSMContext):
        pass
