from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from handlers.support import SupportClass
from utils.states import SelectHotel


__all__ = [
    'MainHandler'
]


class MainHandler(SupportClass):

    def __init__(self):
        super().__init__()
        self._rent_a_room_kb()

    async def main_handler(self, message: Message, state: FSMContext):
        match message.text:

            case 'Орендувати кімнату 🏙':
                await self.rent_a_room(message, state)

            case 'Настройки ⚙️':
                await self.settings(message, state)

            case 'Особистий кабінет 💼':
                await self.user_cabinet(message, state)

            case 'Переглянути історію 🗓':
                await self.check_history(message, state)

            case _:
                await message.answer("Виберіть з меню ⬇️")

    async def rent_a_room(self, message: Message, state: FSMContext):
        state_data = await state.get_data()
        if state_data['CITY'] is None:
            await message.answer(
                "Виберіть місто",
                reply_markup=self._geo_ikb
            )
            await state.set_state(SelectHotel.GET_LOCATION)

        elif state_data['STARS'] is None:
            await message.answer(
                "Шукати готелі з зірковістю",
                reply_markup=self._stars_ikb
            )
            await state.set_state(SelectHotel.SELECT_STARS)

        elif state_data['PRICE_FOR_NIGHT'] is None:
            pass

    async def set_location(self, message: Message, state: FSMContext):
        if message.location:
            user_city = await self.get_city_name(
                message.location.latitude,
                message.location.longitude
            )
            await message.answer(f"Вибрано місто <b>{user_city.capitalize()}</b>", parse_mode='HTML')
            await state.update_data(CITY=user_city.capitalize())

        elif message.text == "Вказати потім ➡️":
            await message.answer("Виведуться міста по всій Україні")
            await state.update_data(CITY='anything')

        elif message.text == "Назад ⤵️":
            await self.main_menu(message, state)

        else:
            await message.answer(f"Вибрано місто <b>{message.text.capitalize()}</b>", parse_mode='HTML')
            await state.update_data(USER_CITY=message.text.capitalize())

        await state.set_state()

    async def set_hotel_stars(self, call: CallbackQuery, state: FSMContext):
        stars_trigger = [f"stars {i}" for i in str(range(1, 5))]
        if call.data in stars_trigger:
            await state.update_data(STARS=int(call.data[-1]))
            await self.rent_a_room(call.message, state)

        elif call.data == 'anything':
            await state.update_data(STARS=call.data)
            await self.rent_a_room(call.message, state)

        elif call.data == "back":
            await self.main_menu(call.message, state)

    async def settings(self, message: Message, state: FSMContext):
        pass

    async def user_cabinet(self, message: Message, state: FSMContext):
        pass

    async def check_history(self, message: Message, state: FSMContext):
        pass
