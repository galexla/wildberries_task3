import logging
import os

from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from db.dals import save_reminder
from utils import (
    ValidationError,
    get_message_history,
    get_previous_user_message,
    parse_validate_reminder_command,
)

log = logging.getLogger("main")
TG_API_TOKEN = os.environ.get("TG_API_TOKEN")
router = Router(name="commands-router")


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    log.debug("cmd_start()")
    await message.answer(
        "Hi there! This is a simple reminder bot. Add it to a chat, post a "
        "message and send /ctrl 5d to post your message again 5 days later.\n"
        "Other period types: h (hour), d (day), w (week), m (month)."
    )


@router.message(Command("ctrl"))
async def cmd_remind(message: types.Message, session: AsyncSession):
    log.debug("cmd_remind()")
    try:
        reminder_date = parse_validate_reminder_command(message.text)
    except ValidationError:
        await message.reply(
            "Please enter reminder date in format 10h, 5d, 1w, 12m "
            "(no more than 10 years in total)."
        )

    history = await get_message_history(TG_API_TOKEN, message.chat.id)
    message = get_previous_user_message(
        history["result"], message.message_id, message.from_user.id
    )
    await save_reminder(session, message, reminder_date)
