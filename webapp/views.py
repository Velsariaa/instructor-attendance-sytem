from django.contrib import messages # type: ignore
from django.http import HttpResponse # type: ignore
from django.utils import timezone # type: ignore
from django.shortcuts import render, redirect , get_object_or_404 # type: ignore
from django.contrib.auth import authenticate, login # type: ignore
from django.contrib.auth.models import User # type: ignore
from .models import  Equipment, UserProfile,UserData, Employee, OrgChartList, TimeRecord,Attendance, Post, DailyTimeRecords,Schedule,History,Comlab,Availability,PositionDCS
from .forms import  ListofstaffForm, OrgChartListForm, ListofstaffForms, TimeRecordForm, PostForm,Dtrc,SuperUserLoginForm,EquipmentForm
from django.contrib.auth.decorators import login_required # type: ignore
from .models import Instructor, Ins_Schedule
from .forms import ScheduleForm
from django.http import Http404
from datetime import datetime
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.db.models import F
from django.http import JsonResponse
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import Employee
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProfile, UserData, Post
from .forms import PostForm
from .models import UserData, Post, UserProfile


def home(request):
    return redirect('user-login')

@csrf_exempt
@login_required
def user_data(request):
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('user_login')

    employee = get_object_or_404(Employee, id=employee_id)  # ✅ Fetch logged-in employee
    user_profile = UserProfile.objects.filter(user=request.user).first()
    user_data = UserData.objects.filter(user=request.user)
    posts = Post.objects.select_related('author').all().order_by('-created_at')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = employee  # ✅ Assign Employee instance instead of User
            post.save()
            return redirect('user_data')
    else:
        form = PostForm()

    return render(request, 'pages/user_data.html', {
        'form': form,
        'user_data': user_data,
        'posts': posts,
        'user_profile': user_profile,
        'first_name': employee.first_name,  # ✅ Pass first_name to the template
    })



@csrf_exempt
@login_required
def UEmployee(request):
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('user_login')
    
    try:
        user_data = UserData.objects.get(user=request.user)
    except UserData.DoesNotExist:
        user_data = None  

    employee = get_object_or_404(Employee, id=employee_id)
    user_profile = UserProfile.objects.filter(user=request.user).first()

    posts = Post.objects.all().order_by('-created_at')

    return render(
        request, 
        'pages/userEmp.html', 
        {
            'user_data': user_data,   
            'user': request.user,      
            'posts': posts,
            'first_name': employee.first_name,  
            'user_profile': user_profile, 
        }
    )

@csrf_exempt
def UEmployeeSched(request):
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('user_login')
    
    try:
        user_data = UserData.objects.get(user=request.user)
    except UserData.DoesNotExist:
        user_data = None  

    employee = get_object_or_404(Employee, id=employee_id)
    user_profile = UserProfile.objects.filter(user=request.user).first()

    # Fetch the schedule data for the logged-in employee
    Sc = Ins_Schedule.objects.filter(employee=employee)

    posts = Post.objects.all().order_by('-created_at')

    return render(
        request, 
        'pages/userEmpSchedule.html', 
        {
            'user_data': user_data,   
            'user': request.user,      
            'posts': posts,
            'first_name': employee.first_name,  
            'user_profile': user_profile,
            'Sc': Sc,  # Pass the schedule data to the template
        }
    )




@csrf_exempt
def create_staff(request):
    if request.method == 'POST':
        form = ListofstaffForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('main') 
    else:
        form = ListofstaffForm()
    return render(request, 'pages/fingerprint_enroll.html', {'form': form})

def main_page(request):
    Ls = Employee.objects.all()
    At = Attendance.objects.all() 
    return render(request, 'pages/main.html', {'Ls': Ls,'At': At})

# def dtr_page(request, pk):
#     employee = get_object_or_404(Employee, pk=pk)
#     current_month = datetime.now().strftime('%B') 
#     attendance_records = Attendance.objects.filter(IdNum=employee.idNum.strip(), date__month=now().month)

#     print(f"Employee ID: {employee.idNum}")
#     print(f"Employee: {employee.first_name} {employee.last_name}")
#     print(f"Attendance records: {attendance_records}")

#     context = {
#         'employee': employee,
#         'At': attendance_records, 
#         'current_month': current_month,
#     }
    
#     return render(request, 'pages/DTR.html', context)


def dtr_page(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    # Get selected month and year from the request, or default to the current month and year
    selected_month = request.GET.get('month', datetime.now().strftime('%B'))
    selected_year = request.GET.get('year', str(datetime.now().year))
    month_number = datetime.strptime(selected_month, '%B').month

    # Fetch attendance records for the selected month and year
    attendance_records = Attendance.objects.filter(
        IdNum=employee.idNum,
        date__month=month_number,
        date__year=int(selected_year),
    )

    DAY_ABBREVIATIONS = {
        'monday': 'M',
        'tuesday': 'T',
        'wednesday': 'W',
        'thursday': 'TH',
        'friday': 'F',
        'saturday': 'S',
        'sunday': 'SU',
    }

    total_undertime_minutes = 0
    attendance_data = []

    for record in attendance_records:
        record_day = record.date.strftime('%A').lower()
        record_day_abbr = DAY_ABBREVIATIONS.get(record_day, '')

        # Retrieve all schedules for the current day, sorted by start time
        schedules = Ins_Schedule.objects.filter(employee=employee, days__icontains=record_day_abbr).order_by('time')

        if schedules.exists() and record.time_out:
            # Get the start time of the first schedule and end time of the last schedule
            earliest_start = schedules.first().time
            latest_end = schedules.last().end_time

            scheduled_start = datetime.combine(record.date, earliest_start)
            scheduled_end = datetime.combine(record.date, latest_end)
            actual_out = datetime.combine(record.date, record.time_out)

            # Check for undertime
            if actual_out < scheduled_end:
                undertime = scheduled_end - actual_out
                undertime_hours = undertime.seconds // 3600
                undertime_minutes = (undertime.seconds % 3600) // 60

                total_undertime_minutes += (undertime_hours * 60) + undertime_minutes
            else:
                undertime_hours = 0
                undertime_minutes = 0
        else:
            # No schedule or missing time_out
            undertime_hours = 'N/A'
            undertime_minutes = 'N/A'

        # Append record data
        attendance_data.append({
            'date': record.date,
            'time_in': record.time_in,
            'time_out': record.time_out,
            'undertime_hours': undertime_hours,
            'undertime_minutes': undertime_minutes,
        })

    # Convert total undertime back to hours and minutes
    total_hours = total_undertime_minutes // 60
    total_minutes = total_undertime_minutes % 60

    # Generate year options dynamically (e.g., from the last 5 years to the next year)
    current_year = datetime.now().year
    year_options = [current_year - i for i in range(5, -1, -1)]  # Last 5 years to this year

    context = {
        'employee': employee,
        'At': attendance_data,
        'current_month': selected_month,
        'current_year': selected_year,
        'total_undertime_hours': total_hours,
        'total_undertime_minutes': total_minutes,
        'months': [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ],
        'years': year_options,
    }
    return render(request, 'pages/DTR.html', context)


def export_dtr_pdf(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    # Fetch the same data as in the `dtr_page` view
    selected_month = request.GET.get('month', datetime.now().strftime('%B'))
    selected_year = request.GET.get('year', str(datetime.now().year))
    month_number = datetime.strptime(selected_month, '%B').month

    attendance_records = Attendance.objects.filter(
        IdNum=employee.idNum,
        date__month=month_number,
        date__year=int(selected_year),
    )

    # Build context similar to `dtr_page`
    context = {
        'employee': employee,
        'At': attendance_records,
        'current_month': selected_month,
        'current_year': selected_year,
        'months': [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ],
        'years': [datetime.now().year - i for i in range(5, -1, -1)],
    }

    # Render the HTML content
    html_string = render_to_string('pages/DTR.html', context)

    # Generate the PDF
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)

    # Return the PDF as a response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{employee.first_name}_{employee.last_name}_DTR.pdf"'
    return response


def attendance_page(request):
    At = Attendance.objects.all()
    Tr = TimeRecord.objects.all()
    sd = Ins_Schedule.objects.all()
    
    
    # Fetch all availability statuses
    availability_data = {
        availability.name: availability.status
        for availability in Availability.objects.all()
    }

    # Pass the availability data to the template
    return render(request, 'pages/attendance.html', {
        'At': At,
        'Tr': Tr,
        'sd': sd,
        'availability_data': availability_data,
    })


def history_page(request):
    cd = History.objects.all()
    return render(request, 'pages/history.html',{'cd': cd})


@csrf_exempt
def dtrm(request):
    At = Attendance.objects.all()    
    Ls = Employee.objects.all()

    
    DTR = DailyTimeRecords.objects.all()
    if request.method == 'POST':
        form = DailyTimeRecords(request.POST)
        if form.is_valid():
            image = form.cleaned_data['image']
            name = form.cleaned_data['name']

            emp = DailyTimeRecords.objects.create(
                image = image,
                name = name
            )

            emp.save()
            return HttpResponse("Saved Successfully")
    form = Dtrc()
    return render(request, 'pages/dtrm.html',{'DTR': DTR , 'form': form, 'At':At, 'Ls':Ls})

@csrf_exempt
def Login(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        User=authenticate(request, username=username,password=password)

        if User is not None:
            login(request, User)
            return redirect('home')
        
        else:
            return HttpResponse("Username or Password is Incorrect.")

    return render(request, 'pages/login.html')


@csrf_exempt
def register(request):
    if request.method=='POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1!=pass2:
            return HttpResponse("Username or Password is incorrect.")
         

        newUser = User.objects.create_user(uname,email,pass1)
        newUser.save()
        return redirect('login')
        
    return render(request, 'pages/registration.html')

@csrf_exempt
def org_chart(request):
    if request.method == 'POST':
        form = OrgChartListForm(request.POST)  
        if form.is_valid():
            form.save()
            return redirect('orgList') 
    else:
        form = OrgChartListForm()
    return render(request, 'pages/orgChart.html', {'form': form})

def org_List(request):
    orgList = OrgChartList.objects.all()
    return render(request, 'pages/orgChartList.html', {'orgList': orgList})

def schedule(request):
    Ls = Employee.objects.all()
    Sc = Ins_Schedule.objects.all()
    return render(request, 'pages/schedule.html',{'Ls':Ls, 'Sc':Sc})

def position(request):
    return render(request, 'pages/position.html')

@csrf_exempt
def edit_employee(request, id):
    listofstaff = get_object_or_404(Employee, id=id)
    if request.method == 'POST':
        form = ListofstaffForms(request.POST, request.FILES, instance=listofstaff)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = ListofstaffForms(instance=listofstaff)
    return render(request, 'pages/edit_employee.html', {'form': form})

def delete_employee(request, id):
    listofstaff = get_object_or_404(Employee, id=id)  
    listofstaff.delete()
    return redirect('main')  

@csrf_exempt
def time_in(request):
    if request.method == 'POST':
        form = TimeRecordForm(request.POST)
        if form.is_valid():
            idNum = form.cleaned_data['idNum']
            employee = Employee.objects.get(idNum=idNum)
            TimeRecord.objects.create(employee=employee, time_in=timezone.now())
            return redirect('employee')
    else:
        form = TimeRecordForm()
    return render(request, 'pages/time_in.html', {'form': form})

@csrf_exempt
def time_out(request):
    if request.method == 'POST':
        form = TimeRecordForm(request.POST)
        if form.is_valid():
            idNum = form.cleaned_data['idNum']
            employee = Employee.objects.get(idNum=idNum)
            time_record = TimeRecord.objects.filter(employee=employee, time_out__isnull=True).first()
            if time_record:
                time_record.time_out = timezone.now()
                time_record.save()
                return redirect('employee')
    else:
        form = TimeRecordForm()
    return render(request, 'pages/time_out.html', {'form': form})

def Logout(request):
    return render(request, 'pages/login.html')

@csrf_exempt
def AdminP(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        User=authenticate(request, username=username,password=password)

        if User is not None:
            login(request, User)
            return redirect('main')
        
        else:
            return HttpResponse("Username or Password is Incorrect.")
    return render(request, 'pages/login.html')


@csrf_exempt
def Udtr(request):
    At = Attendance.objects.all()    
    Ls = Employee.objects.all()

    
    DTR = DailyTimeRecords.objects.all()
    if request.method == 'POST':
        form = DailyTimeRecords(request.POST)
        if form.is_valid():
            image = form.cleaned_data['image']
            name = form.cleaned_data['name']

            emp = DailyTimeRecords.objects.create(
                image = image,
                name = name
            )

            emp.save()
            return HttpResponse("Saved Successfully")
    form = Dtrc()
    return render(request, 'pages/userdtr.html',{'DTR': DTR , 'form': form, 'At':At, 'Ls':Ls})

def HomeView(request):
    post = Post.objects.all()
    post = Post.objects.order_by('-created_at')
    return render (request,'pages/userpanel.html',{'post':post})

@csrf_exempt
@login_required
def createPost(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            return redirect('user_data')  
    else:
        form = PostForm()
    
    return render(request, 'pages/createpost.html', {'form': form})

def Details(request,pk):
    post = Post.objects.get(pk=pk)
    return render(request,'pages/post_detail.html',{'post':post})

@csrf_exempt
@login_required
def Apost(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            try:
                employee = Employee.objects.get(user=request.user)
                post.author = employee  
            except Employee.DoesNotExist:
                post.author = None 
            post.save()
            return redirect('Apost')
    else:
        form = PostForm()

    posts = Post.objects.all().order_by('-created_at')

    return render(request, 'pages/adminPost.html', {
        'form': form,
        'posts': posts,
    })


def adminDetails(request,pk):
    post = Post.objects.get(pk=pk)
    return render (request, 'pages/admin-post-detail.html',{'post':post})

# @login_required  # Ensure only logged-in users can create posts
# def adminCreatP(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES)  # Include request.FILES for image upload
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user  # Assign the current user as the author
#             post.save()  # Save the post
#             return redirect('Apost')  # Redirect to the desired page after saving
#     else:
#         form = PostForm()

#     users = User.objects.all()  # Fetch all users from the database
#     return render(request, 'pages/admin-create-post.html', {'form': form, 'users': users})

@csrf_exempt
def superuser_login(request):
    if request.method == 'POST':
        form = SuperUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('Apost')  # Redirect to dashboard or any other page
            else:
                error_message = "Invalid superuser credentials"
    else:
        form = SuperUserLoginForm()
        error_message = None
    return render(request, 'pages/adminpanel.html', {'form': form, 'error_message': error_message})

@csrf_exempt
def copy_user_data_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        # Get the user data from the Attendance model
        user_data = Attendance.objects.get(id=user_id)
        # Create a new entry in AnotherTable using the user data
        History.objects.create(
            IdNum=user_data.IdNum,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            time_in=user_data.time_in,
            time_out=user_data.time_out,
            date=user_data.date,
            profile_pic=user_data.profile_pic,
        )

        cd = History.objects.all()
        return render(request, 'pages/history.html', {'cd': cd})
    else:
        return redirect('main')
    
def student(request):
    post = Post.objects.all()  
    return render(request, 'pages/student.html', {'post':post})

def studOrg(request):
    orgList = OrgChartList.objects.all()
    return render(request, 'pages/studorgchart.html', {'orgList': orgList})

@csrf_exempt
def comlabA(request):
    # Fetch all equipment entries from the database
    eq = Equipment.objects.all()
    cl = Comlab.objects.all()
    # If the form is submitted, handle the form submission
    if request.method == "POST":
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Acomlab')  

    else:
        form = EquipmentForm()
    return render(request, 'pages/comlab-admin.html', { 'eq': eq,'form': form,'cl': cl,})


def comlabI(request):
    cl = Comlab.objects.all()
    return render(request, 'pages/comlab-ins.html',{'cl':cl})

def landing_page(request):
    return render(request, 'pages/landing_page.html')

def role_selection(request):
    return render(request, 'pages/role_selection.html')

def logout(request):
    return render(request, 'pages/logout.html')
    
def instructor_schedule(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    schedules = Ins_Schedule.objects.filter(instructor=instructor)
    context = {
        'instructor': instructor,
        'schedules': schedules,
    }
    return render(request, 'pages/instructor_schedule.html', context)

@csrf_exempt
def add_schedule(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.instructor = instructor
            schedule.save()
            return redirect('instructor_schedule', instructor_id=instructor.id)
    else:
        form = ScheduleForm()
    return render(request, 'pages/add_edit_schedule.html', {'form': form, 'instructor': instructor})

@csrf_exempt
def edit_schedule(request, schedule_id):
    schedule = get_object_or_404(Ins_Schedule, id=schedule_id)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('instructor_schedule', instructor_id=schedule.instructor.id)
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'pages/add_edit_schedule.html', {'form': form})

@csrf_exempt
def instructor_schedule_view(request, idNum):  # Parameter matches the column name
    try:
        # Query using idNum
        employee = Employee.objects.get(idNum=idNum)
    except Employee.DoesNotExist:
        raise Http404("Employee not found")
    
    # Filter schedules for this employee
    schedules = Ins_Schedule.objects.filter(employee=employee)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.employee = employee  # Link schedule to the employee
            schedule.save()
            return redirect('Ins_Schedule', idNum=employee.idNum)
    else:
        form = ScheduleForm()

    context = {
        'employee': employee,
        'schedules': schedules,
        'form': form,
    }
    return render(request, 'pages/instructor_schedule.html', context)

def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Ins_Schedule, id=schedule_id)
    employee_id = schedule.employee.idNum
    schedule.delete()
    return redirect('Ins_Schedule', idNum=employee_id)

@csrf_exempt
def fingerprint_enroll(request):
    if request.method == 'POST':
        form = ListofstaffForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('main') 
    else:
        form = ListofstaffForm()
    return render(request, 'pages/fingerprint_enroll.html', {'form': form})

def user_login(request):
    error_message = None

    if request.method == "POST":
        idNum = request.POST.get("username")
        password = request.POST.get("password")

        if not idNum or not password:
            error_message = "ID Number and Password are required."
        else:
            try:
                employee = Employee.objects.get(idNum=idNum)
                if employee.password == password:
                    # Create a user session manually
                    request.session['employee_id'] = employee.id
                    request.session['employee_idNum'] = employee.idNum
                    request.session['employee_first_name'] = employee.first_name
                    request.session['employee_last_name'] = employee.last_name
                    return redirect("user_data")  # Redirect on success
                else:
                    error_message = "Invalid ID or password."
            except Employee.DoesNotExist:
                error_message = "Invalid ID or password."

    return render(request, "registration/user-login.html", {"error_message": error_message})

def status_page(request):
    employees = Employee.objects.all()
    whereabouts_choices = dict(Employee.WHEREABOUTS_CHOICES)
    return render(request, 'pages/status.html', {
        'employees': employees,
        'whereabouts_choices': whereabouts_choices
    })

@csrf_exempt
def update_whereabouts(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        new_whereabouts = request.POST.get('whereabouts')
        
        try:
            employee = Employee.objects.get(id=employee_id)
            employee.whereabouts = new_whereabouts
            employee.save()
            return JsonResponse({'status': 'success'})
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)