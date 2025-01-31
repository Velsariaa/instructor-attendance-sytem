from django.db import models # type: ignore
from django.utils import timezone # type: ignore
from django.contrib.auth.models import User # type: ignore


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
class UserData(models.Model):
    profile_id = models.IntegerField(default=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data_field = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pictures', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Existing fields
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    address = models.CharField(max_length=255, null=True, blank=True)  # Assuming you want address in your profile
    date_of_birth = models.DateField(null=True, blank=True)  # You can add date_of_birth if needed
    age = models.IntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    current_workplace = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)

    # New fields
    working_experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"
    
class Attendance(models.Model):
    IdNum = models.CharField(max_length=5, default='')
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    #username = models.CharField(max_length=100, unique=True)
    #email = models.EmailField(unique=True)
    #address = models.TextField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    #gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date = models.DateField(null=True, blank=True)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ('leave', 'Leave'),
        ('in', 'In'),
        ('out', 'Out'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in')  # Adding the status field with choices

    def __str__(self):
        return self.first_name
    
class History(models.Model):
    IdNum = models.CharField(max_length=5, default='')
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    time_in = models.TimeField(null=True, blank=True, default=timezone.now)
    time_out = models.TimeField(null=True, blank=True, default=timezone.now)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    attendance = models.OneToOneField(Attendance, on_delete=models.CASCADE)
    monday_start = models.TimeField(null=True, blank=True)
    monday_end = models.TimeField(null=True, blank=True)
    tuesday_start = models.TimeField(null=True, blank=True)
    tuesday_end = models.TimeField(null=True, blank=True)
    wednesday_start = models.TimeField(null=True, blank=True)
    wednesday_end = models.TimeField(null=True, blank=True)
    thursday_start = models.TimeField(null=True, blank=True)
    thursday_end = models.TimeField(null=True, blank=True)
    friday_start = models.TimeField(null=True, blank=True)
    friday_end = models.TimeField(null=True, blank=True)
    saturday_start = models.TimeField(null=True, blank=True)
    saturday_end = models.TimeField(null=True, blank=True)
    sunday_start = models.TimeField(null=True, blank=True)
    sunday_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Schedule for {self.attendance.IdNum}"

class Employee(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )    
    STATUS_CHOICES = (
        ('Full time', 'Full time'),
        ('Part time', 'Part time'),
        ('Permanent', 'Permanent'),
    )

    POSITION_CHOICES = (
        ('Instructor 1', 'Instructor 1'),
        ('Instructor 2', 'Instructor 2'),
        ('Instructor 3', 'Instructor 3'),
    )
    
    ORGANIZATION_CHOICES = (
        ('Chairperson,DCS', 'Chairperson,DCS'),
        ('Program Chair,CS', 'Program Chair,CS'),
        ('Program Chair, IT', 'Program Chair, IT'),
        ('Instructor', 'Instructor'),
        ('Head, LMS', 'Head, LMS'),
        ('Head, DCS RDE', 'Head, DCS RDE'),
    )
    

    idNum = models.CharField(max_length=20, unique=True, default='')
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    birthday = models.DateField(default='1999-05-24')  # Set the default birthday to May 24, 1999
    age = models.PositiveIntegerField(default='')  # Set the default age to 25
    status = models.CharField(max_length=20,  default='', choices=STATUS_CHOICES)
    position = models.CharField(max_length=20,default='', choices=POSITION_CHOICES)
    profile = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='')
    organization = models.CharField(max_length=50,default='', choices= ORGANIZATION_CHOICES)
    fingerprint_id = models.CharField(max_length=20, null=True, blank=True)
    backup_fingerprint_id = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.first_name
     
class TimeRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)


class DailyTimeRecords(models.Model):
    image = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class OrgChartList(models.Model):
    profile = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)
    title = models.TextField(blank=True)
    # Add the on_delete argument to the OneToOneField
    position_dcs = models.OneToOneField('PositionDCS', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    
class PositionDCS(models.Model):
    positions = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.positions

class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(blank=True)  # Allow the body field to be empty
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='profile_pics', null=True, blank=True)

    def __str__(self):
        return f"{self.title} | {self.author}"


class SuperUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    equipment = models.CharField(max_length=100)
    date = models.DateTimeField()  # Use DateTimeField to store both date and time

    def __str__(self):
        return self.name
    

class Comlab(models.Model):
    cards = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    comlab = models.CharField(max_length=50, null=True, blank=True)

class Availability(models.Model):
    STATUS_CHOICES = (
        ('In', 'In'),
        ('Out', 'Out'),
        ('On Class', 'On Class'),
        ('On Break', 'On Break'),
        ('On Leave', 'On Leave'),
        ('Absent', 'Absent'),
    )
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20,  default='', choices=STATUS_CHOICES)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Ins_Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='idNum')
    subject_code = models.CharField(max_length=20)  # Add subject code field
    subject = models.CharField(max_length=100)
    section = models.CharField(max_length=50)
    days = models.CharField(max_length=20)  # Ensure this is a CharField
    time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.subject} ({self.days})"