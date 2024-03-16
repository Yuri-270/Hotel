from aiogram.fsm.state import StatesGroup, State


__all__ = [
    'RegistrationState'
]


class RegistrationState(StatesGroup):
    INPUT_FIRST_NAME = State()
