from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from sqlalchemy import create_engine

jobstores = {}
executors = {"default": ProcessPoolExecutor(2)}
job_defaults = {
    "coalesce": True,
}
scheduler = AsyncIOScheduler(
    executors=executors,
    job_defaults=job_defaults,
    timezone=utc,
)


def initialize_scheduler(db_url: str):
    sync_engine = create_engine(db_url)
    jobstores["default"] = SQLAlchemyJobStore(engine=sync_engine)
    scheduler.configure(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=utc,
    )
    scheduler.start()
