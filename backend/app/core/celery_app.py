from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "hypercode_worker",
    broker=settings.HYPERCODE_REDIS_URL,
    backend=settings.HYPERCODE_REDIS_URL
)

celery_app.conf.task_routes = {
    "app.worker.test_celery": "main-queue"
}
