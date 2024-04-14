from aiogram.fsm.state import StatesGroup, State


__all__ = [
    'RegistrationState'
]


class RegistrationState(StatesGroup):
    INPUT_FIRST_NAME = State()
    INPUT_SECOND_NAME = State()
    INPUT_BIRTHDAY = State()
    INPUT_PASSPORT_DATA = State()
