from .registration import RegistrationHandler
from .main_handler import MainHandler
from .rent_a_room import RentARoom
from .user_cabinet import UserCabinet
from .view_room import ViewRoom


__all__ = [
    'registration_handler_class',
    'main_handler_class',
    'rent_a_room_class',
    'user_cabinet_class',
    'view_room_class'
]


registration_handler_class = RegistrationHandler()
user_cabinet_class = UserCabinet()
main_handler_class = MainHandler()
rent_a_room_class = RentARoom()
view_room_class = ViewRoom()
