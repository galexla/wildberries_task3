import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import commands
import config
from db.dals import get_reminders_after_date, set_reminder_sent
from middlewares import DbSessionMiddleware
from scheduler import initialize_scheduler, scheduler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

bot = None


async def send_reminders():
    async with async_sessionmaker(
        create_async_engine(config.DB_URL)
    )() as session:
        log.debug("Sending reminders...")
        reminders = await get_reminders_after_date(
            session, datetime.now(timezone.utc)
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
    global bot
    bot = Bot(config.TG_API_TOKEN)
    # bot_username = (await bot.get_me()).username

    engine = create_async_engine(config.DB_URL, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    # dp.update.middleware(StripMentionMiddleware(bot_username))
    dp.include_router(commands.router)

    initialize_scheduler()
    job_id = "send_reminders_job"
    if not scheduler.get_job(job_id):
        scheduler.add_job(send_reminders, "interval", seconds=10, id=job_id)

    # @dp.message()
    # async def handle_message(message: types.Message):
    #     log.info(
    #         f"Received message: {message.text} from {message.from_user.id}"
    #     )

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
