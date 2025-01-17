from django import forms # type: ignore
from .models import Employee, OrgChartList, Post, UserData, Equipment,Availability
from .models import Ins_Schedule

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
    class Meta:
        model = Ins_Schedule
        fields = ['subject', 'section', 'days', 'time', 'room']