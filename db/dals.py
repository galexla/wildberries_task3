from datetime import datetime

from aiogram import types
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import LastMessage, Reminder


async def save_reminder(
    session: AsyncSession, message: types.Message, reminder_date: datetime
):
    async with session:
        instance = Reminder(
            tg_message_id=message.message_id,
            tg_chat_id=message.chat.id,
            tg_user_id=message.from_user.id,
            text=message.text,
            remind_at=reminder_date,
        )
        session.add(instance)
        await session.commit()


async def get_reminders_after_date(session: AsyncSession, date: datetime):
    stmt = select(Reminder).where(
        Reminder.remind_at >= date, Reminder.is_sent == False
    )
    result = await session.execute(stmt)
    reminders = result.scalars().all()
    return reminders


async def set_reminder_sent(session: AsyncSession, reminder: Reminder):
    reminder.is_sent = True
    await session.commit()


async def add_message_keep_last_two(
    session: AsyncSession, message: types.Message
):
    async with session:
        stmt = (
            select(LastMessage)
            .where(
                LastMessage.tg_chat_id == message.chat.id,
                LastMessage.tg_user_id == message.from_user.id,
            )
            .order_by(LastMessage.id.desc())
        )
        result = await session.execute(stmt)
        last_message = result.scalars().first()

        instance = LastMessage(
            tg_message_id=message.message_id,
            tg_chat_id=message.chat.id,
            tg_user_id=message.from_user.id,
            text=message.text,
        )
        session.add(instance)
        await session.flush()
        await session.refresh(instance)

        ids = [instance.id]
        if last_message is not None:
            ids.append(last_message.id)

        stmt = delete(LastMessage).where(
            LastMessage.tg_chat_id == message.chat.id,
            LastMessage.tg_user_id == message.from_user.id,
            LastMessage.id.not_in(ids),
        )
        await session.execute(stmt)

        await session.commit()
