from celery import Celery
from config import settings

app = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)