import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import commands
from db.dals import get_reminders_after_date, set_reminder_sent
from middlewares import DbSessionMiddleware
from scheduler import initialize_scheduler, run_async_job, scheduler

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

load_dotenv(".env")
TG_API_TOKEN = os.environ.get("TG_API_TOKEN")
DB_URL = os.environ.get("DB_URL")

bot = None


async def send_reminders():
    async with async_sessionmaker(create_async_engine(DB_URL))() as session:
        log.debug("Sending reminders...")
        reminders = await get_reminders_after_date(
            session, datetime.now(datetime.UTC)
        )
        for reminder in reminders:
            log.debug("Sending reminder[%s]", reminder.id)
            message = await bot.send_message(
                reminder.tg_chat_id,
                reminder.text,
                reply_to_message_id=reminder.tg_message_id,
            )
            if message:
                await set_reminder_sent(session, reminder)
        log.info("Sent %s reminder(s)", len(reminders))


async def main():
    engine = create_async_engine(url=DB_URL, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    global bot
    bot = Bot(TG_API_TOKEN)

    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.include_router(commands.router)

    await initialize_scheduler(DB_URL)
    scheduler.add_job(
        lambda: run_async_job(send_reminders), "interval", seconds=10
    )

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
