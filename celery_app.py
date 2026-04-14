# celery_app.py
from celery import Celery
import config

def make_celery():
    celery = Celery(
        'meeting_backend',
        broker=config.CELERY_BROKER_URL,
        backend=config.CELERY_RESULT_BACKEND
    )
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Jakarta",
        enable_utc=True,
    )
    return celery

celery = make_celery()
