import asyncio
import logging

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import commands
import config
from middlewares import DbSessionMiddleware
from scheduler import initialize_scheduler, scheduler, send_reminders

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

bot = None


async def main():
    global bot
    bot = Bot(config.TG_API_TOKEN)

    engine = create_async_engine(config.DB_URL, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.include_router(commands.router)

    initialize_scheduler()
    job_id = "send_reminders_job"
    if not scheduler.get_job(job_id):
        scheduler.add_job(
            send_reminders, "interval", [bot], seconds=10, id=job_id
        )

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
