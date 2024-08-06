import logging

from aiogram import Router
from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

import config
from db.dals import add_message_keep_last_two, save_reminder
from utils import (
    ValidationError,
    get_bot_command,
    get_message_history,
    get_period_name,
    get_previous_user_message,
    parse_validate_reminder_command,
)

log = logging.getLogger("commands")

router = Router(name="commands-router")


class CommandFilter(Filter):
    def __init__(self, command: str):
        self.command = command

    async def __call__(self, message: Message) -> bool:
        bot_username = "@" + (await message.bot.me()).username
        text = message.text.strip()
        if not text.startswith(bot_username):
            return False
        text = text[len(bot_username) :].strip()
        return text.startswith(self.command)


@router.message(CommandFilter("/start"))
async def cmd_start(message: Message):
    log.debug("cmd_start()")
    await message.answer(
        "Hi there! This is a simple reminder bot. Add it to a chat, post a "
        "message and send /ctrl 5d to post your message again 5 days later.\n"
        "Other period types: h (hour), d (day), w (week), m (month)."
    )


@router.message(CommandFilter("/ctrl"))
async def cmd_remind(message: Message, session: AsyncSession):
    log.debug("cmd_remind()")
    try:
        command = get_bot_command(message)
        reminder_date, number, period = parse_validate_reminder_command(
            command
        )
        period_name = get_period_name(period)
    except ValidationError:
        await message.reply(
            "Please enter reminder date in format 10h, 5d, 1w, 12m "
            "(no more than 10 years in total)."
        )
        return

    response = await get_message_history(config.TG_API_TOKEN, message.chat.id)
    if not response["ok"]:
        await message.reply(
            "Some error occured. You may be in a private chat. Please add "
            "this bot to a public chat."
        )
        return

    message = get_previous_user_message(
        response["result"], message.message_id, message.from_user.id
    )
    await save_reminder(session, message, reminder_date)
    await message.reply(
        "#Task# is accepted. I will remind you about it after "
        f"{number} {period_name}"
    )


@router.message()
async def msg(message: Message, session: AsyncSession):
    await add_message_keep_last_two(session, message)
