from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from handlers.support import SupportClass
from utils.data_base import DataBase
from utils.states import ViewRoomState


__all__ = [
    'ViewRoom'
]


class ViewRoom(SupportClass):

    def __init__(self):
        super().__init__()
        self._view_room_kbs()

    async def check_booking(self, message: Message, state: FSMContext, bot: Bot):
        await self.delete_reply_kb(message, bot)

        pool = await DataBase.get_pool()
        async with pool.acquire() as con:
            state_data = await state.get_data()
            booking_data = await con.fetchrow(
                "SELECT * FROM booking WHERE user_id = $1 AND date_of_departure < CURRENT_DATE",
                state_data['USER_ID']
            )
            room_data = await con.fetchrow(
                """SELECT in_hotel, price_for_night, for_how_many_people
                FROM rooms WHERE id = $1""",
                booking_data['room_id']
            )
            await state.update_data(HOTEL_ID=room_data['in_hotel'])
            hotel_data = await con.fetchrow(
                """SELECT city, address, stars FROM hotels WHERE hotel_id = $1""",
                room_data['in_hotel']
            )

            last_message = await message.answer(
                f"""Бронювання №<code>{booking_data['booking_id']}</code>

Адреса: <i>{hotel_data['city']} {hotel_data['address']}</i>
Зірковість готелю: <b>{hotel_data['stars']}</b>
На скількох розрахований номер: <b>{room_data['for_how_many_people']}</b>

Дата заїзду: <i><b>{booking_data['date_of_arrival']:%d.%m.%Y}</b></i>
Дата виїзду: <i><b>{booking_data['date_of_departure']:%d.%m.%Y}</b></i>

Ціна: <b>{room_data['price_for_night']*(booking_data['date_of_departure']-booking_data['date_of_arrival']).days}</b>""",
                parse_mode=ParseMode.HTML,
                reply_markup=self._view_room_kb
            )
            await state.update_data(LAST_MESSAGE=last_message)
            await state.set_state(ViewRoomState.VIEW_ROOM_HANDLER)

    async def view_menu_handler(self, call: CallbackQuery, state: FSMContext, bot: Bot):
        state_data = await state.get_data()
        last_message = state_data['LAST_MESSAGE']
        await bot.delete_message(chat_id=last_message.chat.id, message_id=last_message.message_id)

        pool = await DataBase.get_pool()
        async with pool.acquire() as con:
            if call.data == "order_a_service":
                unlocked_services_id = await con.fetch(
                    "SELECT service_id FROM additional_services_in_hotel WHERE hotel_id = $1",
                    state_data['HOTEL_ID']
                )
                all_services = await con.fetch(
                    "SELECT * FROM additional_services"
                )

                unlocked_services_data = list()
                for unlocked_service in unlocked_services_id:
                    unlocked_services_data.append(all_services[unlocked_service[0]-1])

                # Construct message
                message_text = "ID | Назва | Ціна"
                i = 1
                for unlocked_service_data in unlocked_services_data:
                    message_text += f"\n<b>{i}</b> | "
                    message_text += f"{unlocked_service_data[1]} | "
                    message_text += f"<b>{unlocked_service_data[2]}</b>"
                    i += 1

                ikb = await self._get_service_kb(len(unlocked_services_data))
                last_message = await call.message.answer(
                    message_text,
                    reply_markup=ikb,
                    parse_mode=ParseMode.HTML
                )
                await state.update_data(LAST_MESSAGE=last_message)
                await state.set_state(ViewRoomState.SELECTED_SERVICE_HANDLER)

            elif call.data == "cancel_your_reservation":
                ...

            elif call.data == "extend_your_reservation":
                ...

            elif call.data == "back":
                await self.main_menu(call.message, state)

    async def service_name_handler(self, call: CallbackQuery, state: FSMContext, bot: Bot):
        state_data = await state.get_data()
        last_message = state_data['LAST_MESSAGE']
        await bot.delete_message(chat_id=last_message.chat.id, message_id=last_message.message_id)

        call_number = (range(1, 5))
        if call.data == "back":
            await self.check_booking(call.message, state, bot)

        elif int(call.data) in call_number:
            pool = await DataBase.get_pool()
            async with pool.acquire() as con:
                service_data = await con.fetchrow(
                    "SELECT service_name, price FROM additional_services WHERE id = $1",
                    int(call.data)
                )
                await con.fetch(
                    "INSERT INTO active_additional_services VALUES($1, $2)",
                    int(call.data)-1,
                    state_data["HOTEL_ID"]
                )
            await call.message.answer(
                f"Послуга <i>{service_data[0]}</i> за <b>{service_data[1]}</b> замовлена",
                parse_mode=ParseMode.HTML
            )
            await self.main_menu(call.message, state)
