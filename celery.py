from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AMSUFB.settings')

app = Celery('webapp')
app.config_from_object('django.conf.settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'archive_employee_data_daily':{
        'task':'webapp.tasks.archive_employee_data',
        'schedule': crontab(hour=0, minute=0),
    }
}