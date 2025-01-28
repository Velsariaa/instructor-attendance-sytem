from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from webapp .models import Attendance, Employee
from django.utils import timezone # type: ignore
from django.db.models import Q

def index(request):
    return render(request, 'pages/fingerprint_control.html')


@api_view(['GET', 'POST'])
def is_active(request):
    cache_key = 'fingerprint_active'
    
    if request.method == 'POST':
        active_state = request.data.get('is_active', False)  # Make this toggleable
        cache.set(cache_key, active_state, timeout=None)  
        return Response({'status': 'success', 'is_active': active_state})
        
    if request.method == 'GET':
        is_active = cache.get(cache_key, False)   # Make this toggleable
        return Response({'is_active': is_active})
    

@api_view(['GET', 'POST'])
def mode(request):
    cache_key = 'fingerprint_mode'
    
    if request.method == 'POST':
        mode_state = request.data.get('mode', 'verify')   # Make this toggleable
        cache.set(cache_key, mode_state, timeout=None)  
        return Response({'status': 'success', 'mode': mode_state})
        
    if request.method == 'GET':
        current_mode = cache.get(cache_key, 'verify')  # Make this toggleable
        return Response({'mode': current_mode})


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

            # Extract the required details
            first_name = employee.first_name
            middle_name = employee.middle_name
            last_name = employee.last_name

            # Check if there's an existing attendance record for today without a timeout
            today = timezone.now().date()
            attendance = Attendance.objects.filter(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                date=today,
                time_out__isnull=True  # Ensure no timeout has been set
            ).first()

            if attendance:
                # Update the existing record with time out and status out
                attendance.time_out = timezone.now().time()
                attendance.status = "Out"
                attendance.save()
            else:
                # Create a new attendance record with time in and status in
                attendance = Attendance(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    date=today,
                    time_in=timezone.now().time(),
                    status="In"
                )
                attendance.save()
        except Employee.DoesNotExist:
            return render(request, 'pages/error.html', {'error': 'Employee not found.'})

    return render(request, 'pages/main.html')


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



