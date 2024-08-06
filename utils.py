from datetime import datetime, timezone

import aiohttp
from aiogram.types import Message
from dateutil.relativedelta import relativedelta


class ValidationError(Exception):
    pass


def parse_validate_reminder_command(text: str) -> tuple[datetime, int, str]:
    number, period = parse_reminder_command(text)
    reminder_date = calc_reminder_date(
        datetime.now(timezone.utc), number, period
    )
    validate_reminder_date(reminder_date)
    return reminder_date, number, period


def parse_reminder_command(text: str) -> tuple[int, str]:
    text = text.strip().lower()
    text = text[6:].strip()

    if not 2 <= len(text) <= 6:
        raise ValidationError

    period_name = text[-1]
    number = text[:-1]
    if not number.isdigit():
        raise ValidationError

    number = int(number)
    if number <= 0:
        raise ValidationError

    if period_name not in "hdwm":
        raise ValidationError

    return number, period_name


def get_bot_command(message: Message):
    """Get comment without any leading text"""
    for entity in message.entities:
        if entity.type == "bot_command":
            return message.text[entity.offset :]
    return message.text


def get_period_name(period: str) -> str:
    mapping = {"h": "hours", "d": "days", "w": "weeks", "m": "months"}
    return mapping[period]


def get_period_name_ru(period: str) -> str:
    mapping = {"h": "часов", "d": "дней", "w": "недель", "m": "месяцев"}
    return mapping[period]


def calc_reminder_date(date: datetime, number: int, period: str) -> datetime:
    period_name = get_period_name(period)
    kwargs = {period_name: number}
    return date + relativedelta(**kwargs)


def validate_reminder_date(date: datetime) -> bool:
    if date > datetime.now(timezone.utc) + relativedelta(years=10):
        raise ValidationError()
