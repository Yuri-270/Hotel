from aiogram.types import Message


__all__ = [
    'SupportClass'
]


class SupportClass:

    def __init__(self):
        pass

    @staticmethod
    async def _length_checker(message: Message, length_of_message: int) -> bool:
        if len(message.text) <= length_of_message:
            return True

        else:
            last_word = 'символів'
            if length_of_message % 10 == 1:
                last_word = 'символа'

            await message.answer(f"Повідомлення має містити менше {length_of_message} {last_word}")

            return False
