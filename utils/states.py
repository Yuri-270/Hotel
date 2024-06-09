from aiogram.fsm.state import StatesGroup, State


__all__ = [
    'RegistrationState',
    'MainState',
    'SelectHotel',
    'ViewRoomState',
    'UserCabinetState'
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
    RENT_A_ROOM_HANDLER = State()
    RENT_A_SELECTED_ROOM_HANDLER = State()
    SET_DATE_OF_ARRIVAL = State()
    SET_DATE_OF_DEPARTURE = State()
    CONFIRM_RESERVATIONS = State()


class ViewRoomState(StatesGroup):
    VIEW_ROOM_HANDLER = State()
    SELECTED_SERVICE_HANDLER = State()
    DELETE_BOOKING = State()


class UserCabinetState(StatesGroup):
    USER_CABINET_HANDLER = State()
    INPUT_EMAIL = State()
    CONFIRM_EMAIL = State()
    INPUT_PHONE_NUMBER = State()
    CONFIRM_PASSPORT_DATA = State()
    SET_PASSPORT_NUMBER = State()
    SET_PASSPORT_VALID_UNTIL = State()
