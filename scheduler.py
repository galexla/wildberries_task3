from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

jobstores = {
    "default": SQLAlchemyJobStore(url="sqlite+aiosqlite:///jobs.sqlite")
}
executors = {"default": ProcessPoolExecutor(2)}
job_defaults = {
    "coalesce": True,
}
scheduler: BackgroundScheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=utc,
)
