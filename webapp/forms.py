from django import forms # type: ignore
from .models import Employee, OrgChartList, Post, UserData, Equipment, Availability
from .models import Ins_Schedule
import datetime  # Add this import

class Dtrc(forms.Form):
    image  = forms.ImageField(label='Profile Picture', required=False)
    name = forms.CharField()

class ListofstaffForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['idNum', 'first_name', 'last_name', 'middle_name', 'birthday', 'status', 'position', 'profile','age', 'gender','organization']

class OrgChartListForm(forms.ModelForm):
    class Meta:
        model = OrgChartList
        fields = '__all__' 

class ListofstaffForms(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['idNum', 'first_name', 'last_name', 'middle_name', 'birthday', 'age', 'status', 'position', 'profile', 'gender', 'organization']

class TimeRecordForm(forms.Form):
    idNum = forms.CharField(max_length=20)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body', 'image']

class SuperUserLoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'equipment', 'date']  # Define the fields to be displayed in the form
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Ensure date input type is rendered correctly in HTML
        }

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['name', 'status']
        widgets = {
            'status': forms.Select(choices=Availability.STATUS_CHOICES)
        }

class AvailabilityEditForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['name', 'status']
        widgets = {
            'status': forms.Select(choices=Availability.STATUS_CHOICES)
        }

class UserDataForm(forms.ModelForm):
    class Meta:
        model = UserData
        fields = '__all__'  # List the fields you want to include in the form

class ScheduleForm(forms.ModelForm):
    DAYS_CHOICES = [
        ('M', 'Monday'),
        ('T', 'Tuesday'),
        ('W', 'Wednesday'),
        ('TH', 'Thursday'),
        ('F', 'Friday'),
        ('S', 'Saturday'),
        ('SU', 'Sunday'),
    ]

    days = forms.MultipleChoiceField(choices=DAYS_CHOICES, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Ins_Schedule
        fields = ['subject', 'section', 'days', 'time', 'end_time', 'room']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_days(self):
        days = self.cleaned_data.get('days')
        return ''.join(days)  # Convert list of days to a concatenated string

    def clean_time(self):
        time = self.cleaned_data.get('time')
        if isinstance(time, datetime.time):
            return time.isoformat()
        return time

    def clean_end_time(self):
        end_time = self.cleaned_data.get('end_time')
        if isinstance(end_time, datetime.time):
            return end_time.isoformat()
        return end_time