from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.support import SupportClass
from handlers.rent_a_room import RentARoom
from utils.states import SelectHotel


__all__ = [
    'MainHandler'
]


class MainHandler(SupportClass):
    rent_a_room_class = RentARoom()

    def __init__(self):
        super().__init__()
        self._rent_a_room_kb()

    async def main_handler(self, message: Message, state: FSMContext, bot: Bot):
        match message.text:

            case 'Орендувати кімнату 🏙':
                await self.rent_a_room(message, state, bot)

            case 'Настройки ⚙️':
                await self.settings(message, state)

            case 'Особистий кабінет 💼':
                await self.user_cabinet(message, state)

            case 'Переглянути історію 🗓':
                await self.check_history(message, state)

            case _:
                await message.answer("Виберіть з меню ⬇️")

    async def rent_a_room(self, message: Message, state: FSMContext, bot: Bot):
        state_data = await state.get_data()
        if state_data['CITY'] is None:
            await message.answer(
                "Виберіть місто",
                reply_markup=self._geo_ikb
            )
            await state.set_state(SelectHotel.GET_LOCATION)

        else:
            await self.rent_a_room_class.get_hotels(message, state)

    async def set_location(self, message: Message, state: FSMContext, bot: Bot):
        if message.location:
            user_city = await self.get_city_name(
                message.location.latitude,
                message.location.longitude
            )
            await message.answer(f"Вибрано місто <b>{user_city.capitalize()}</b>", parse_mode='HTML')
            await state.update_data(CITY=user_city.capitalize())
            await self.rent_a_room(message, state, bot)

        elif message.text == "На головне меню ⤵️":
            await self.main_menu(message, state)

        else:
            await message.answer(f"Вибрано місто <b>{message.text.capitalize()}</b>", parse_mode='HTML')
            await state.update_data(CITY=message.text.capitalize())
            await self.rent_a_room(message, state, bot)

    async def settings(self, message: Message, state: FSMContext):
        pass

    async def user_cabinet(self, message: Message, state: FSMContext):
        pass

    async def check_history(self, message: Message, state: FSMContext):
        pass
