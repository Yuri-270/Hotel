from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart

from utils.states import *
import handlers


__all__ = [
    'router'
]


router = Router()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    await handlers.registration_handler_class.command_start(message, state)


@router.message()
async def state_commands(message: Message, state: FSMContext, bot: Bot):
    user_state = await state.get_state()
    match user_state:

        # Registration handlers
        case RegistrationState.INPUT_FIRST_NAME:
            await handlers.registration_handler_class.set_first_name(message, state)
        case RegistrationState.INPUT_SECOND_NAME:
            await handlers.registration_handler_class.set_second_name(message, state)
        case RegistrationState.INPUT_BIRTHDAY:
            await handlers.registration_handler_class.set_birthday(message, state)
        case RegistrationState.INPUT_EMAIL:
            await handlers.registration_handler_class.set_email(message, state, bot)
        case RegistrationState.VERIFICATION_EMAIL:
            await handlers.registration_handler_class.check_verification_email_key(message, state)
        case RegistrationState.INPUT_TELEPHONE_NUMBER:
            await handlers.registration_handler_class.set_telephone_number(message, state)
        case RegistrationState.INPUT_PASSPORT_NUMBER:
            await handlers.registration_handler_class.get_passport_data(message, state)
        case RegistrationState.INPUT_PASSPORT_VALID_UNTIL:
            await handlers.registration_handler_class.get_passport_valid_until(message, state)

        # Main handlers
        case MainState.MAIN_HANDLER:
            await handlers.main_handler_class.main_handler(message, state, bot)
        case SelectHotel.GET_LOCATION:
            await handlers.main_handler_class.set_location(message, state)
        case SelectHotel.SET_DATE_OF_ARRIVAL:
            await handlers.rent_a_room_class.set_date_of_arrival(message, state)
        case SelectHotel.SET_DATE_OF_DEPARTURE:
            await handlers.rent_a_room_class.set_date_of_departure(message, state)

        # View room

        # User cabinet
        case UserCabinetState.INPUT_EMAIL:
            await handlers.user_cabinet_class.set_email(message, state, bot)
        case UserCabinetState.CONFIRM_EMAIL:
            await handlers.user_cabinet_class.confirm_email(message, state, bot)
        case UserCabinetState.INPUT_PHONE_NUMBER:
            await handlers.user_cabinet_class.set_new_phone_number(message, state, bot)
        case UserCabinetState.SET_PASSPORT_NUMBER:
            await handlers.user_cabinet_class.passport_valid_until_menu(message, state, bot)
        case UserCabinetState.SET_PASSPORT_VALID_UNTIL:
            await handlers.user_cabinet_class.set_passport_valid_until(message, state, bot)

        case _:
            await message.answer("Спочатку введіть /start")


@router.callback_query()
async def callback_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.answer()
    user_state = await state.get_state()
    match user_state:
        case RegistrationState.CONFIRM_THE_TRANSFER_PASSPORT_DATA:
            await handlers.registration_handler_class.input_passport_number(call, state)
        case SelectHotel.RENT_A_ROOM_HANDLER:
            await handlers.rent_a_room_class.rent_a_room_handler(call, state, bot)
        case SelectHotel.RENT_A_SELECTED_ROOM_HANDLER:
            await handlers.rent_a_room_class.rent_a_selected_room_handler(call, state, bot)
        case SelectHotel.CONFIRM_RESERVATIONS:
            await handlers.rent_a_room_class.confirm_payment(call, state, bot)
        case UserCabinetState.USER_CABINET_HANDLER:
            await handlers.user_cabinet_class.user_cabinet_handler(call, state, bot)
        case UserCabinetState.CONFIRM_PASSPORT_DATA:
            await handlers.user_cabinet_class.passport_number_menu(call, state, bot)
        case ViewRoomState.VIEW_ROOM_HANDLER:
            await handlers.view_room_class.view_menu_handler(call, state, bot)
        case ViewRoomState.SELECTED_SERVICE_HANDLER:
            await handlers.view_room_class.service_name_handler(call, state, bot)
        case ViewRoomState.DELETE_BOOKING:
            await handlers.view_room_class.delete_booking(call, state, bot)
