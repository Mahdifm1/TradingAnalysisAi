import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings')

app = Celery('trading_platform')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
