from aiogram.fsm.state import StatesGroup, State


__all__ = [
    'RegistrationState',
    'MainState',
    'SelectHotel'
]


class RegistrationState(StatesGroup):
    INPUT_FIRST_NAME = State()
    INPUT_SECOND_NAME = State()
    INPUT_BIRTHDAY = State()
    INPUT_EMAIL = State()
    VERIFICATION_EMAIL = State()


class MainState(StatesGroup):
    MAIN_HANDLER = State()


class SelectHotel(StatesGroup):
    GET_LOCATION = State()
