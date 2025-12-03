from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.REDIS_URL)

celery_app.conf.task_routes = {
    "app.workers.tasks.send_email": "main-queue",
    "app.workers.tasks.send_sms": "main-queue",
}
