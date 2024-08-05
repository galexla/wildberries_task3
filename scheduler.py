import asyncio

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from sqlalchemy import create_engine

executors = {"default": ThreadPoolExecutor(1)}

job_defaults = {"coalesce": True}

scheduler = AsyncIOScheduler(
    executors=executors, job_defaults=job_defaults, timezone=utc
)


def initialize_scheduler(db_url: str):
    sync_engine = create_engine(db_url, future=True)
    jobstores = {"default": SQLAlchemyJobStore(engine=sync_engine)}
    scheduler.configure(jobstores=jobstores)
    scheduler.start()


def run_async_job(coroutine_func):
    loop = asyncio.get_event_loop()
    loop.create_task(coroutine_func)
