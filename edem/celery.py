from __future__ import absolute_import
import os
from celery import Celery
from datetime import timedelta

from celery import shared_task
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edem.settings')

from django.conf import settings  # noqa
app = Celery('edem')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

from celery.schedules import crontab
@shared_task
def add():
    return 4 + 5



CELERYBEAT_SCHEDULE = {
    # Executes every day morning at 00:05 A.M
    'add-every-day': {
        'task': 'create',
        'schedule': crontab(hour=00, minute=05),
    },
    'add-every-30-seconds': {
        'task': 'add',
        'schedule': timedelta(seconds=30),
    },
}

CELERY_TIMEZONE = 'UTC'
