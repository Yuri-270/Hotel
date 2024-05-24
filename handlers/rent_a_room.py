from datetime import datetime

from aiogram import Bot
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
        self._rent_a_room_kb()

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
            await state.update_data(ROOMS_INFO=all_rooms)

            rooms_str = '<b>№</b> | ⭐️ | Ціна за ніч\n'
            i = 1
            for room in all_rooms:
                hotel_id = await con.fetchval("SELECT in_hotel FROM rooms WHERE id = $1", room[0])
                star = await con.fetchval("SELECT stars FROM hotels WHERE hotel_id = $1", hotel_id)
                rooms_str += f'<b>{i}</b> | {star} | <i>{room[1]}</i>\n'
                i += 1

        ikb = await self._rent_a_room_kb_builder(len(all_rooms))
        last_message = await message.answer(
            rooms_str,
            parse_mode=ParseMode.HTML,
            reply_markup=ikb
        )
        await state.update_data(LAST_MESSAGE=last_message)
        await state.set_state(SelectHotel.RENT_A_ROOM_HANDLER)

    async def rent_a_room_handler(self, call: CallbackQuery, state: FSMContext, bot: Bot):
        state_data = await state.get_data()

        # Delete last message
        last_message: Message = state_data["LAST_MESSAGE"]
        await bot.delete_message(chat_id=last_message.chat.id, message_id=last_message.message_id)

        rooms_info = state_data['ROOMS_INFO']
        callback_data = [str(i) for i in range(1, len(rooms_info) + 1)]

        if call.data in callback_data:
            await self.delete_reply_kb(call.message, bot)
            pool = await DataBase.get_pool()
            async with pool.acquire() as con:
                selected_room_id = rooms_info[int(call.data)-1]

                # price, street, star, for people
                room_data = await con.fetchrow(
                    """SELECT in_hotel, price_for_night, for_how_many_people 
                    FROM rooms WHERE id = $1 AND status = 'Ready to receive'""",
                    selected_room_id[0]
                )
                hotel_data = await con.fetchrow(
                    "SELECT city, address, stars FROM hotels WHERE hotel_id = $1",
                    room_data['in_hotel']
                )
                await state.update_data(ROOM_INFO=room_data)

                user_message = f"""Ціна за ніч 🏙: <b>{room_data['price_for_night']}</b>
Адреса 🗺: <b><i>{hotel_data['city']} {hotel_data['address']}</i></b>
Зірок ⭐️: <b>{hotel_data['stars']}</b>
На скільки людей розрахована 🖐: <b>{room_data['for_how_many_people']}</b>"""

                friend_lease = await con.fetchval(
                    "SELECT date_of_arrival FROM booking WHERE room_id = $1",
                    selected_room_id[0]
                )
                if friend_lease is not None:
                    today_date = datetime.today().date()
                    num_of_night = friend_lease - today_date
                    num_of_night = num_of_night.days - 1

                    if num_of_night % 10 == 1:
                        num_of_night_str = 'ніч'
                    elif 1 < num_of_night % 10 < 5:
                        num_of_night_str = 'ночі'
                    else:
                        num_of_night_str = 'ночей'
                    user_message += f"\n\nМожна орендувати на <b>{num_of_night}</b> {num_of_night_str}"
                    user_message += f" до <b>{friend_lease:%d.%m.%Y}</b>"

                await call.message.answer(
                    user_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=self._do_rent_a_room_ikb
                )
                await state.set_state(SelectHotel.RENT_A_SELECTED_ROOM_HANDLER)

        elif call.data == "Change_city":
            await call.message.answer(
                "Виберіть місто",
                reply_markup=self._geo_ikb
            )
            await state.set_state(SelectHotel.GET_LOCATION)

        elif call.data == "In_main_menu":
            await self.main_menu(call.message, state)

    async def rent_a_selected_room_handler(self, call: CallbackQuery, state: FSMContext):
        pass
