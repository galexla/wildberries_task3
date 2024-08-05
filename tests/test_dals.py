from datetime import datetime
from unittest.mock import MagicMock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dals import get_reminders_after_date, save_reminder, set_reminder_sent
from db.models import Reminder


async def test_save_reminder(db_session: AsyncSession):
    message = MagicMock()
    message.message_id = 123
    message.chat.id = 20
    message.from_user.id = 10
    message.text = "text1"
    date = datetime.fromisoformat("2024-07-30 00:00:00")
    await save_reminder(db_session, message, date)

    result = await db_session.execute(
        select(Reminder).filter(
            Reminder.tg_message_id == 123,
            Reminder.tg_chat_id == 20,
            Reminder.tg_user_id == 10,
            Reminder.text == "text1",
            Reminder.remind_at == date,
        )
    )
    reminder = result.scalars().first()
    assert reminder is not None
    assert reminder.tg_message_id == 123
    assert reminder.tg_chat_id == 20
    assert reminder.tg_user_id == 10
    assert reminder.text == "text1"
    assert reminder.remind_at == date


async def test_get_reminders_after_date(db_session: AsyncSession):
    date = datetime.fromisoformat("2024-08-04 21:00:00")
    reminders = await get_reminders_after_date(db_session, date)
    assert len(reminders) == 2
    assert reminders[0].id == 2
    assert reminders[0].remind_at == datetime.fromisoformat(
        "2024-08-05 08:22:00"
    )
    assert reminders[1].id == 3
    assert reminders[1].remind_at == datetime.fromisoformat(
        "2024-08-05 10:22:00"
    )


async def test_set_reminder_sent(db_session: AsyncSession):
    result = await db_session.execute(
        select(Reminder).filter(Reminder.id == 2)
    )
    reminder = result.scalars().first()
    await set_reminder_sent(db_session, reminder)
    result = await db_session.execute(
        select(Reminder).filter(Reminder.id == 2)
    )
    reminder = result.scalars().first()
    assert reminder.is_sent == True
