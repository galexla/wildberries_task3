import logging

from aiogram import Router
from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

import config
from db.dals import (
    add_message_keep_last_two,
    get_last_user_message,
    save_reminder,
)
from utils import (
    ValidationError,
    get_bot_command,
    get_period_name_ru,
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
        "Привет! Это простой бот-напоминалка. Добавьте его в чат. Отправьте "
        "любое сообщение и затем команду /ctrl 5d - бот перепостит это "
        "сообщение 5 дней спустя.\n"
        "Вот все виды периодов: h (часы), d (дни), w (недели), m (месяцы)."
    )


@router.message(CommandFilter("/ctrl"))
async def cmd_remind(message: Message, session: AsyncSession):
    log.debug("cmd_remind()")
    try:
        command = get_bot_command(message)
        reminder_date, number, period = parse_validate_reminder_command(
            command
        )
        period_name = get_period_name_ru(period)
    except ValidationError:
        await message.reply(
            "Пожалуйста, введите дату напоминания в формате 10h, 5d, 1w, 12m "
            "(но в сумме не более 10 лет)."
        )
        return

    last_message = await get_last_user_message(
        session, message.chat.id, message.from_user.id
    )
    if last_message is None:
        await last_message.reply(
            "Предыдущих сообщений пользователя не найдено."
        )
        return
    await save_reminder(session, last_message, reminder_date)
    await message.reply(
        f"#Задача# принята. Напомню о ней через {number} {period_name}."
    )


@router.message()
async def msg(message: Message, session: AsyncSession):
    await add_message_keep_last_two(session, message)
