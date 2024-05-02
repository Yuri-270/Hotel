from .registration import RegistrationHandler
from .main_handler import MainHandler


__all__ = [
    'registration_handler_class',
    'main_handler_class'
]


registration_handler_class = RegistrationHandler()
main_handler_class = MainHandler()
