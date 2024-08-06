import logging
from datetime import datetime, timezone

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import config
from db.dals import get_reminders_before_date, set_reminder_sent

log = logging.getLogger("scheduler")
executors = {"default": ThreadPoolExecutor(1)}

job_defaults = {"coalesce": True}

scheduler = AsyncIOScheduler(
    executors=executors, job_defaults=job_defaults, timezone=utc
)


def initialize_scheduler():
    jobstores = {
        "default": MemoryJobStore(),
    }
    scheduler.configure(jobstores=jobstores)
    scheduler.start()


async def send_reminders(bot):
    async with async_sessionmaker(
        create_async_engine(config.DB_URL)
    )() as session:
        log.debug("Sending reminders...")
        reminders = await get_reminders_before_date(
            session, datetime.now(timezone.utc)
        )
        for reminder in reminders:
            await session.refresh(reminder)
            log.debug("Sending reminder[%s]", reminder.id)
            message = await bot.send_message(
                reminder.tg_chat_id,
                reminder.text,
                reply_to_message_id=reminder.tg_message_id,
            )
            if message:
                await set_reminder_sent(session, reminder)
        log.info("Sent %s reminder(s)", len(reminders))
