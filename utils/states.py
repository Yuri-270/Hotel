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
    INPUT_TELEPHONE_NUMBER = State()
    CONFIRM_THE_TRANSFER_PASSPORT_DATA = State()
    INPUT_PASSPORT_NUMBER = State()
    INPUT_PASSPORT_VALID_UNTIL = State()


class MainState(StatesGroup):
    MAIN_HANDLER = State()


class SelectHotel(StatesGroup):
    GET_LOCATION = State()
    SELECT_STARS = State()
    SET_STARTING_PRICE = State()
    SET_FINISHING_PRICE = State()
    SET_FOR_HOW_MANY_PEOPLE = State()
