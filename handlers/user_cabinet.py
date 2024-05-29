from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.support import SupportClass


__all__ = [
    "UserCabinet"
]


class UserCabinet(SupportClass):

    def __init__(self):
        super().__init__()

    async def user_cabinet_handler(self, call: CallbackQuery, state: FSMContext):
        pass
