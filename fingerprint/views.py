from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status


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


@api_view(['POST'])
def enroll(request):
    if request.method == 'POST':
        fingerprint_data = JSONParser().parse(request)
        print("Received fingerprint data:", fingerprint_data)
        
        response_data = {
            'success': True,
            'main': fingerprint_data.get('main'),
            'backup': fingerprint_data.get('backup')
        }
        
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request method'})
 
@api_view(['POST'])
def verify(request):
    if request.method == 'POST':
        match_id = JSONParser().parse(request)
        print(match_id)
    return render(request, 'pages/test.html')


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



