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
            ...
        case _:
            await message.answer("Спочатку введіть /start")
