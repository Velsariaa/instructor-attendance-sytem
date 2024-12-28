from celery import shared_task
from django.core.management import call_command

def archive_employee_data():
    call_command('AMSUFB', 'webapp')