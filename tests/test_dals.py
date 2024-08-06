from datetime import datetime
from unittest.mock import MagicMock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dals import (add_message_keep_last_two, get_last_user_message,
                     get_reminders_before_date, save_reminder,
                     set_reminder_sent)
from db.models import LastMessage, Reminder


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
    reminders = await get_reminders_before_date(db_session, date)
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


async def test_add_message_keep_last_two(db_session: AsyncSession):
    data = [
        {
            "values": {"message_id": 6, "chat_id": 1, "user_id": 125},
            "expected": {"ids": set([6, 3]), "texts": set(["text6", "text3"])},
        },
        {
            "values": {"message_id": 7, "chat_id": 1, "user_id": 123},
            "expected": {"ids": set([7, 5]), "texts": set(["text7", "text5"])},
        },
        {
            "values": {"message_id": 8, "chat_id": 3, "user_id": 120},
            "expected": {"ids": set([8]), "texts": set(["text8"])},
        },
    ]

    for elem in data:
        message = MagicMock()
        message.message_id = elem["values"]["message_id"]
        message.chat.id = elem["values"]["chat_id"]
        message.from_user.id = elem["values"]["user_id"]
        message.text = f"text{elem['values']['message_id']}"
        await add_message_keep_last_two(db_session, message)

        stmt = select(LastMessage).where(
            LastMessage.tg_chat_id == message.chat.id,
            LastMessage.tg_user_id == message.from_user.id,
        )
        result = await db_session.execute(stmt)
        messages = result.scalars().fetchall()
        ids = set([msg.id for msg in messages])
        assert ids == elem["expected"]["ids"]
        texts = set([msg.text for msg in messages])
        assert texts == elem["expected"]["texts"]


# def test_get_last_user_message():
#     messages = [
#         {"message": {"id": 0, "from": {"id": 1}}},
#         {"message": {"id": 1, "from": {"id": 1}}},
#         {"message": {"id": 2, "from": {"id": 1}}},
#         {"message": {"id": 3, "from": {"id": 1}}},
#         {"message": {"id": 4, "from": {"id": 2}}},
#         {"message": {"id": 5, "from": {"id": 3}}},
#     ]
#     message = get_last_user_message(messages, 2, 1)
#     assert message["message"]["id"] == 1

#     message = get_last_user_message(messages, 1, 1)
#     assert message["message"]["id"] == 0

#     message = get_last_user_message(messages, 0, 1)
#     assert message is None

#     message = get_last_user_message(messages, 5, 3)
#     assert message is None
