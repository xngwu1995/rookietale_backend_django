import os

from celery import Celery
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twitter.settings')

app = Celery('twitter')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'get-latest-vcp-strategy': {
        'task': 'stocks.tasks.get_latest_vcp_strategy',
        'schedule': crontab(hour=6, minute=15, day_of_week='1-5'),
    },
    'get-async-options': {
        'task': 'stocks.tasks.get_async_options',
        'schedule': crontab(hour=8, minute=41, day_of_week='1-5'),
    },
}