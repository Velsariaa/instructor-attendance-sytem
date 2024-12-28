from django.core.management.base import BaseCommand
from webapp.models import Employee, ArchivedData
from django.utils import timezone

class Command(BaseCommand):
    help = 'Delete employee data older than a day and archives it'

    def handle(self,*args, **kwargs):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)
        employees_to_archive = Employee.objects.filter(date__lt=one_day_ago)


        for employee in employees_to_archive:
            ArchivedData.objects.create(
                profile_pic = employee.profile_pic,
                first_name = employee.first_name,
                last_name = employee.last_name,
                username = employee.username,
                email = employee.email,
                address = employee.address,
                gender = employee.gender,
                time_in = employee.time_in,
                time_out = employee.time_out,
                date = employee.date,
            )

            employees_to_archive.delete()



