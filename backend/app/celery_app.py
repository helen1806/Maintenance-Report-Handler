import os
from celery import Celery

# Default to localhost for local development
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "nexusmaint_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["app.services.worker_tasks"]

)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
