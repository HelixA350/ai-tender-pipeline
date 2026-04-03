import os
from celery import Celery
from api.config import settings

celery_app = Celery("worker", broker=settings.rabbitmq_url)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_backend=None,
    imports=("worker.tasks",),
)
