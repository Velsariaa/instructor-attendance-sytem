from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from webapp .models import Attendance, Employee, Ins_Schedule
from django.utils import timezone # type: ignore
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pytz

@csrf_exempt
def index(request):
    return render(request, 'pages/fingerprint_control.html')


@csrf_exempt
@api_view(['GET', 'POST'])
def is_active(request):
    cache_key = 'fingerprint_active'
    
    if request.method == 'POST':
        active_state = request.data.get('is_active', True)  
        cache.set(cache_key, active_state, timeout=None)  
        return Response({'status': 'success', 'is_active': active_state})
        
    if request.method == 'GET':
        is_active = cache.get(cache_key, True)   
        return Response({'is_active': is_active})


@csrf_exempt
@api_view(['GET', 'POST'])
def mode(request):
    cache_key = 'fingerprint_mode'
    
    if request.method == 'POST':
        mode_state = request.data.get('mode', 'verify')   
        cache.set(cache_key, mode_state, timeout=None)  
        return Response({'status': 'success', 'mode': mode_state})
        
    if request.method == 'GET':
        current_mode = cache.get(cache_key, 'verify')  
        return Response({'mode': current_mode})



@csrf_exempt
@api_view(['POST', 'GET'])
def enroll(request):
    cache_key = 'fingerprint_enrollment_data'
    
    if request.method == 'POST':
        fingerprint_data = JSONParser().parse(request)
        print("Received fingerprint data:", fingerprint_data)
        
        response_data = {
            'success': True,
            'main': fingerprint_data.get('main'),
            'backup': fingerprint_data.get('backup')
        }
        
        cache.set(cache_key, response_data, timeout=None)  
        return JsonResponse(response_data)
    elif request.method == 'GET':
      
        response_data = cache.get(cache_key, {})
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'})
 
@csrf_exempt
@api_view(['POST'])
def verify(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        match_id = data.get('match_id')

        try:
            # Check if match_id matches either fingerprint_id or backup_fingerprint_id
            employee = Employee.objects.get(
                Q(fingerprint_id=match_id) | Q(backup_fingerprint_id=match_id)
            )

            # Extract details
            first_name = employee.first_name
            middle_name = employee.middle_name
            last_name = employee.last_name
            idNum = employee.idNum

            # Get today's date and current time in Philippine Time (PHT)
            philippines_timezone = pytz.timezone('Asia/Manila')
            today = timezone.now().astimezone(philippines_timezone).date()
            current_time = timezone.now().astimezone(philippines_timezone).time()

            # Find earliest schedule time
            schedules = Ins_Schedule.objects.filter(employee=employee)
            min_schedule_time = min((schedule.time for schedule in schedules), default=None)

            status = "In"
            if min_schedule_time and current_time > min_schedule_time:
                status = "Late"

            # Check existing attendance without timeout
            attendance = Attendance.objects.filter(
                IdNum=idNum,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                date=today,
                time_out__isnull=True  # Ensure no timeout has been set
            ).first()

            if attendance:
                # If the employee was late at clock-in, mark the clock-out status as "Late" as well
                if status == "Late":
                    attendance.status = "Late"
                attendance.time_out = timezone.now().astimezone(philippines_timezone).time()
                attendance.save()
            else:
                # Create a new attendance record with time in and dynamic status
                attendance = Attendance(
                    IdNum=idNum,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    date=today,
                    time_in=timezone.now().astimezone(philippines_timezone).time(),
                    status=status
                )
                attendance.save()
        except Employee.DoesNotExist:
            return render(request, 'pages/error.html', {'error': 'Employee not found.'})

    return render(request, 'pages/main.html')



@csrf_exempt
@api_view(['GET', 'POST'])
def delete_all(request):
    cache_key = 'fingerprint_delete_all'
    
    if request.method == 'POST':
        delete_state = request.data.get('delete_all', False)
        cache.set(cache_key, delete_state, timeout=None)  # Store indefinitely
        return Response({'status': 'success', 'delete_all': delete_state})
        
    if request.method == 'GET':
        should_delete = cache.get(cache_key, False)  # Default to False if not set
        # Reset the delete flag after it's been read
        if should_delete:
            cache.set(cache_key, False, timeout=None)
        return Response({'delete_all': should_delete})


@csrf_exempt
@api_view(['GET', 'POST'])
def enrollment_status(request):
    cache_key = 'fingerprint_enrollment_status'
    
    if request.method == 'POST':
        status_data = {
            'status': request.data.get('status', 'idle'),  # idle/success/fail
            'message': request.data.get('message', ''),
            'finger': request.data.get('finger', 'main')  # main/backup
        }
        cache.set(cache_key, status_data, timeout=None)
        return Response({'status': 'success'})
        
    if request.method == 'GET':
        status_data = cache.get(cache_key, {
            'status': 'idle',
            'message': 'Waiting for finger placement...',
            'finger': 'main'
        })
        return Response(status_data)



