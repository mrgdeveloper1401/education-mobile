import os

from celery import Celery
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "base.settings")

app = Celery("base.utils")

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
