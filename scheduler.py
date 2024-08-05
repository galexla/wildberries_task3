from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

executors = {"default": ThreadPoolExecutor(1)}

job_defaults = {"coalesce": True}

scheduler = AsyncIOScheduler(
    executors=executors, job_defaults=job_defaults, timezone=utc
)


def initialize_scheduler(db_url: str):
    jobstores = {
        "default": MemoryJobStore(),
    }
    scheduler.configure(jobstores=jobstores)
    scheduler.start()
