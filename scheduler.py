import asyncio

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

jobstores = {}
executors = {"default": ThreadPoolExecutor(1)}
job_defaults = {
    "coalesce": True,
}
scheduler = AsyncIOScheduler(
    executors=executors,
    job_defaults=job_defaults,
    timezone=utc,
)


async def initialize_scheduler(db_url: str):
    sync_engine = create_async_engine(db_url)
    jobstores["default"] = SQLAlchemyJobStore(engine=sync_engine.sync_engine)
    scheduler.configure(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=utc,
    )
    await sync_engine.dispose()
    scheduler.start()


def run_async_job(coroutine_func):
    loop = asyncio.get_event_loop()
    loop.create_task(coroutine_func)
