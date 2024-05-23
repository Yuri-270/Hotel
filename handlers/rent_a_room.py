from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from utils.data_base import DataBase
from utils.states import SelectHotel
from handlers.support import SupportClass


__all__ = [
    "RentARoom"
]


class RentARoom(SupportClass):

    def __init__(self):
        super().__init__()

    async def get_hotels(self, message: Message, state: FSMContext):
        """Get hotels by city"""
        state_data = await state.get_data()
        selected_city_name = state_data['CITY']  # Get selected city

        pool = await DataBase.get_pool()
        async with pool.acquire() as con:
            # Get hotels id in selected city
            hotels_id = await con.fetch("SELECT hotel_id FROM hotels WHERE city = $1", selected_city_name)
            all_rooms = list()
            for hotel_id in hotels_id:
                rooms = await con.fetch(
                    """SELECT id, price_for_night from rooms 
                    WHERE in_hotel = $1 AND status = 'Ready to receive'""",
                    hotel_id[0]
                )
                all_rooms.extend(rooms)

            # Sorted by price for night
            all_rooms = sorted(all_rooms, key=lambda x: x['price_for_night'], reverse=True)

            # number, stars, price
            rooms_str = '<b>№</b> | ⭐️ | Ціна за ніч\n'
            i = 1
            for room in all_rooms:
                hotel_id = await con.fetchval("SELECT in_hotel FROM rooms WHERE id = $1", room[0])
                star = await con.fetchval("SELECT stars FROM hotels WHERE hotel_id = $1", hotel_id)
                rooms_str += f'<b>{i}</b> | {star} | <i>{room[1]}</i>\n'
                i += 1

        ikb = await self._rent_a_room_kb_builder(len(all_rooms))
        await message.answer(
            rooms_str,
            parse_mode=ParseMode.HTML,
            reply_markup=ikb
        )
        await state.set_state(SelectHotel.RENT_A_ROOM_HANDLER)

    async def rent_a_room_handler(self, call: CallbackQuery, state: FSMContext):
        pass
