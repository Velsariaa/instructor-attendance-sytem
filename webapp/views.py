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


def home(request):
    return redirect('user-login')

@login_required
def user_data(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
 
    user_profile = UserProfile.objects.filter(user=request.user).first()
    user_data = UserData.objects.filter(user=request.user)  
    posts = Post.objects.select_related('author').all().order_by('-created_at')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('user_data')
    else:
        form = PostForm()

    return render(request, 'pages/user_data.html', {
        'form': form,
        'user_data': user_data,
        'posts': posts,
        'user_profile': user_profile
    })

def create_staff(request):
    if request.method == 'POST':
        form = ListofstaffForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('main') 
    else:
        form = ListofstaffForm()
    return render(request, 'pages/addEmp.html', {'form': form})

def main_page(request):
    Ls = Employee.objects.all()
    At = Attendance.objects.all() 
    return render(request, 'pages/main.html', {'Ls': Ls,'At': At})

def dtr_page(request, pk ):
    Ls = Employee.objects.get(id=pk)
    Tr = TimeRecord.objects.all()

    return render(request, 'pages/DTR.html', { 'Ls':Ls, 'Tr':Tr})

def attendance_page(request):
    At = Attendance.objects.all()
    Tr = TimeRecord.objects.all()
    sd = Schedule.objects.all()
    
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
    return render(request, 'pages/schedule.html',{'Ls':Ls})

def position(request):
    return render(request, 'pages/position.html')

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


@login_required
def UEmployee(request):
    try:
        user_data = UserData.objects.get(user=request.user)
    except UserData.DoesNotExist:
        user_data = None  
    posts = Post.objects.all().order_by('-created_at')
    return render(
        request, 
        'pages/userEmp.html', 
        {
            'user_data': user_data,   
            'user': request.user,      
            'posts': posts,            
        }
    )


@login_required
def UEmployeeSched(request):
    try:
        user_data = UserData.objects.get(user=request.user)
    except UserData.DoesNotExist:
        user_data = None
    posts = Post.objects.all().order_by('-created_at')
    
    return render(request, 'pages/userEmpSchedule.html', {'user_data': user_data,'user': request.user, 'posts': posts, })
    

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

@login_required
def Apost(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    user_data = UserData.objects.filter(user=request.user)  
    posts = Post.objects.select_related('author').all().order_by('-created_at')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('Apost')
    else:
        form = PostForm()

    return render(request, 'pages/adminPost.html', {
        'form': form,
        'user_data': user_data,
        'posts': posts,
        'user_profile': user_profile
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