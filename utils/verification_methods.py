from datetime import datetime, timedelta
from email.mime.text import MIMEText
from random import randint as rand

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import smtplib

from utils.data_base import DataBase
from main import Settings


__all__ = [
    'VerifyingEmail'
]


class VerifyingMethods:

    @classmethod
    async def _generate_verification_key(cls, state: FSMContext) -> str:
        """Generate and get verifying key"""
        verifying_key = str(rand(1, 999999))
        i = len(verifying_key)
        while i < 6:
            verifying_key = '0' + verifying_key
            i += 1

        await state.update_data(VERIFYING_EMAIL_KEY=verifying_key)

        return verifying_key

    @classmethod
    async def _set_key_lifetime(cls, state: FSMContext) -> datetime:
        """Get key lifetime"""
        today_date = datetime.now()
        to_code_active = today_date + timedelta(hours=1)
        await state.update_data(VERIFYING_EMAIL_KEY_ACTIVE=to_code_active)

        return to_code_active


class VerifyingEmail(VerifyingMethods):

    @classmethod
    async def send_message(cls, message: Message, state: FSMContext):
        gmail_data = await Settings.get_gmail_data()

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        try:
            server.login(gmail_data[0], gmail_data[1])

            to_code_active = await cls._set_key_lifetime(state)  # Set key life
            verifying_key = await cls._generate_verification_key(state)  # Generate verifying key

            # Generate message
            email_message = MIMEText(
                f"""Це повідомлення було згенероване для верифікації аккаунту в<br>
telegram боті https://t.me/DoorsInUkraineBot
<h2><b>{verifying_key}</b></h2>
Даний код дійсний до {to_code_active.date()} {to_code_active.strftime("%H:%M:%S")}""",
                'html'
            )
            email_message['Subject'] = "Hotel Ukraine"
            server.sendmail(gmail_data[0], message.text, email_message.as_string())

        except Exception as _ex:
            print(f'error {_ex}')

    @classmethod
    async def check_verifying_key(cls, message: Message, state: FSMContext) -> bool:
        """Return True if verification key is right and not overdue"""
        state_data = await state.get_data()
        today_date = datetime.today()

        if today_date <= state_data['VERIFYING_EMAIL_KEY_ACTIVE'] and message.text == state_data['VERIFYING_EMAIL_KEY']:
            pool = await DataBase.get_pool()
            async with pool.acquire() as con:
                await con.fetch(
                    "UPDATE users SET email = $2 WHERE id = $1",
                    state_data['USER_ID'],
                    state_data['EMAIL']
                )

            return True

        else:
            await message.answer("Даний код недійсний")

        return False
