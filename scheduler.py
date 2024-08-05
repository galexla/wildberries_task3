from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

jobstores = {
    "default": SQLAlchemyJobStore(url="sqlite+aiosqlite:///jobs.sqlite")
}
executors = {"default": ProcessPoolExecutor(2)}
job_defaults = {
    "coalesce": True,
}
scheduler: AsyncIOScheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=utc,
)
