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
                    """SELECT id, in_hotel, price_for_night, for_how_many_people 
                    FROM rooms WHERE id = $1 AND status = 'Ready to receive'""",
                    selected_room_id[0]
                )
                hotel_data = await con.fetchrow(
                    "SELECT city, address, stars FROM hotels WHERE hotel_id = $1",
                    room_data['in_hotel']
                )
                await state.update_data(ROOM_INFO=room_data)
                await state.update_data(HOTEL_INFO=hotel_data)

                user_message = f"""Ціна за ніч 🏙: <b>{room_data['price_for_night']}</b>
Адреса 🗺: <b><i>{hotel_data['city']}, {hotel_data['address']}</i></b>
Зірок ⭐️: <b>{hotel_data['stars']}</b>
На скільки людей розрахована 🖐: <b>{room_data['for_how_many_people']}</b>"""

                friend_lease = await con.fetch(
                    "SELECT date_of_arrival, date_of_departure FROM booking WHERE room_id = $1",
                    selected_room_id[0]
                )
                await state.update_data(FRIEND_LEASE=friend_lease)
                if len(friend_lease) != 0:
                    user_message += f"\n\nНомер вже заброньований на період:"
                    for one_lease in friend_lease:
                        user_message += f"\n<b>{one_lease[0]:%d.%m.%Y} - {one_lease[1]:%d.%m.%Y}</b>"

                last_message = await call.message.answer(
                    user_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=self._do_rent_a_room_ikb
                )
                await state.update_data(LAST_MESSAGE=last_message)
                await state.set_state(SelectHotel.RENT_A_SELECTED_ROOM_HANDLER)

        elif call.data == "Change_city":
            await call.message.answer(
                "Виберіть місто",
                reply_markup=self._geo_ikb
            )
            await state.set_state(SelectHotel.GET_LOCATION)

        elif call.data == "In_main_menu":
            await self.main_menu(call.message, state)

    async def rent_a_selected_room_handler(self, call: CallbackQuery, state: FSMContext, bot: Bot):
        state_data = await state.get_data()
        last_message: Message = state_data["LAST_MESSAGE"]
        await bot.delete_message(chat_id=last_message.chat.id, message_id=last_message.message_id)

        if call.data == "Back":
            await self.get_hotels(call.message, state)

        elif call.data == "Rent":
            await call.message.answer(
                "Вкажіть дату заїзду",
                reply_markup=self._back_kb
            )
            await state.set_state(SelectHotel.SET_DATE_OF_ARRIVAL)

    async def set_date_of_arrival(self, message: Message, state: FSMContext):
        if message.text == "Назад ⬅️":
            await self.get_hotels(message, state)
            return None

        date_res = await self._date_checker(message, message.text)
        if date_res[0]:
            today_date = datetime.today().date()
            if today_date < date_res[1]:
                state_data = await state.get_data()

                if len(state_data['FRIEND_LEASE']) != 0:
                    for one_lease in state_data['FRIEND_LEASE']:
                        if one_lease[0] <= date_res[1] <= one_lease[1]:
                            break
                    else:
                        await state.update_data(DATE_OF_ARRIVAL=date_res[1])

                        await message.answer(
                            "Введіть дату виїзду",
                            reply_markup=self._back_kb
                        )
                        await state.set_state(SelectHotel.SET_DATE_OF_DEPARTURE)
                        return None
                    await message.answer("Указана дата вже заброньована")

            else:
                await message.answer("Указана дата неактуальна")

    async def set_date_of_departure(self, message: Message, state: FSMContext):
        if message.text == "Назад ⬅️":
            await message.answer(
                "Вкажіть дату заїзду",
                reply_markup=self._back_kb
            )
            await state.set_state(SelectHotel.SET_DATE_OF_ARRIVAL)

        date_res = await self._date_checker(message, message.text)
        if date_res[0]:
            today_date = datetime.today().date()
            if today_date < date_res[1]:
                state_data = await state.get_data()

                if len(state_data['FRIEND_LEASE']) != 0:
                    for one_lease in state_data['FRIEND_LEASE']:
                        if one_lease[0] <= date_res[1] <= one_lease[1]:
                            break
                    else:
                        await state.update_data(DATE_OF_DEPARTURE=date_res[1])
                        await self.__outcomes_of_lease(message, state)  # Confirm payment
                        return None
                    await message.answer("Указана дата вже заброньована")

            else:
                await message.answer("Указана дата неактуальна")

    async def __outcomes_of_lease(self, message: Message, state: FSMContext):
        state_data = await state.get_data()
        room_address = state_data['ROOM_INFO']
        hotel_address = state_data['HOTEL_INFO']
        date_of_arrival = state_data['DATE_OF_ARRIVAL']
        date_of_departure = state_data['DATE_OF_DEPARTURE']

        if (date_of_departure - date_of_arrival).days >= 0:
            gap = (date_of_departure - date_of_arrival).days
        else:
            gap = date_of_arrival - date_of_departure
            await state.update_data(DATE_OF_ARRIVAL=date_of_departure)
            await state.update_data(DATE_OF_DEPARTURE=date_of_arrival)

        await message.answer(
            f"""Забронювати кімнату в: 
<b><i>{hotel_address[0]}, {hotel_address[1]}</i></b>
на период <b>{date_of_arrival:%d.%m.%Y} - {date_of_departure:%d.%m.%Y}</b>

Ціна: <b>{room_address['price_for_night']*(gap+1)}</b>""",
            reply_markup=self._confirm_payment_ikb,
            parse_mode=ParseMode.HTML
        )
        await state.set_state(SelectHotel.CONFIRM_RESERVATIONS)

    async def confirm_payment(self, call: CallbackQuery, state: FSMContext):
        if call.data == "cancel":
            await self.main_menu(call.message, state)

        elif call.data == "confirm":
            pool = await DataBase.get_pool()
            async with pool.acquire() as con:
                state_data = await state.get_data()
                await con.fetch(
                    "INSERT INTO booking(user_id, room_id, date_of_arrival, date_of_departure) VALUES ($1, $2, $3, $4)",
                    state_data['USER_ID'],
                    state_data['ROOM_INFO']["id"],
                    state_data['DATE_OF_ARRIVAL'],
                    state_data['DATE_OF_DEPARTURE']
                )
            await call.message.answer("Ваш номер заброньований")
            await self.main_menu(call.message, state)
