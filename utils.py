from datetime import datetime

import aiohttp
from dateutil.relativedelta import relativedelta


class ValidationError(Exception):
    pass


def parse_validate_reminder_command(text: str) -> datetime:
    number, period = parse_reminder_command(text)
    reminder_date = calc_reminder_date(datetime.now(), number, period)
    validate_reminder_date(reminder_date)
    return reminder_date


def parse_reminder_command(text: str) -> tuple[int, str]:
    text = text.strip().lower()
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


def calc_reminder_date(date: datetime, number: int, period: str) -> datetime:
    mapping = {"h": "hours", "d": "days", "w": "weeks", "m": "months"}
    kwargs = {mapping[period]: number}
    return date + relativedelta(**kwargs)


def validate_reminder_date(date: datetime) -> bool:
    if date > datetime.now() + relativedelta(years=10):
        raise ValidationError()


async def get_message_history(
    api_token: str, chat_id, offset: int = 0, limit: int = 100
) -> list[dict]:
    url = f"https://api.telegram.org/bot{api_token}/messages.getHistory"
    payload = {
        "chat_id": chat_id,
        "offset": offset,
        "limit": limit,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()


def get_previous_user_message(
    messages: list[dict], message_id, user_id
) -> dict | None:
    """
    Get a message of user_id previous to message_id
    """
    n = len(messages)
    i = n - 1
    while i >= 0:
        if messages[i]["message"]["id"] == message_id:
            break
        i -= 1
    else:
        return None

    j = i - 1
    while j >= 0:
        if messages[j]["message"]["from"]["id"] == user_id:
            return messages[j]
        j -= 1

    return None
