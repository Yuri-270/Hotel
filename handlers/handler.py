from aiogram import Router, Bot
from aiogram.types import Message
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
        case RegistrationState.INPUT_FIRST_NAME:
            await handlers.registration_handler_class.set_first_name(message, state)
        case RegistrationState.INPUT_SECOND_NAME:
            await handlers.registration_handler_class.set_second_name(message, state)
        case RegistrationState.INPUT_BIRTHDAY:
            await handlers.registration_handler_class.set_birthday(message, state)
        case RegistrationState.INPUT_EMAIL:
            await handlers.registration_handler_class.set_email(message, state)
        case RegistrationState.VERIFICATION_EMAIL:
            await handlers.registration_handler_class.check_verification_email_key(message, state)
        case MainState.MAIN_HANDLER:
            await handlers.main_handler_class.main_handler(message, state)
        case SelectHotel.GET_LOCATION:
            await handlers.main_handler_class.set_location(message, state)
        case RegistrationState.INPUT_TELEPHONE_NUMBER:
            await handlers.registration_handler_class.set_telephone_number(message, state)
        case _:
            await message.answer("Спочатку введіть /start")
