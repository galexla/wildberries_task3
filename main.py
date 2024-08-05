import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

from db.dals import get_reminders_after_date, save_reminder, set_reminder_sent
from db.session import async_session
from scheduler import scheduler
from utils import (
    ValidationError,
    get_message_history,
    get_previous_user_message,
    parse_validate_reminder_command,
)

logging.basicConfig(level=logging.INFO)
load_dotenv(".env")

TG_API_TOKEN = os.environ.get("TG_API_TOKEN")
bot = Bot(token=TG_API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["ctrl"])
async def remind(message: types.Message):
    try:
        reminder_date = parse_validate_reminder_command(message.text)
    except ValidationError:
        await message.reply(
            "Пожалуйста, введите дату напоминания в формате 10h, 5d, 1w, 12m "
            "(не более чем на 10 лет вперед)."
        )

    history = await get_message_history(TG_API_TOKEN, message.chat.id)
    message = get_previous_user_message(
        history["result"], message.message_id, message.from_user.id
    )
    await save_reminder(async_session, message, reminder_date)


async def send_reminders():
    reminders = get_reminders_after_date(
        async_session, datetime.now(datetime.UTC)
    )
    for reminder in reminders:
        message = await bot.send_message(
            reminder.tg_chat_id,
            reminder.text,
            reply_to_message_id=reminder.tg_message_id,
        )
        if message:
            set_reminder_sent(async_session, reminder)


if __name__ == "__main__":
    # executor.start_polling(dp, skip_updates=True)
    dp.start_polling(dp, skip_updates=True)
    job = scheduler.add_job(send_reminders, "interval", minutes=1)
