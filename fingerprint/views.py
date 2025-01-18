from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status


def index(request):
    return render(request, 'pages/test.html')

def mode():
    pass

@api_view(['GET', 'POST'])
def is_active(request):
    cache_key = 'fingerprint_active'
    
    if request.method == 'POST':
        active_state = request.data.get('is_active', False)
        cache.set(cache_key, active_state, timeout=None)  
        return Response({'status': 'success', 'is_active': active_state})
        
    if request.method == 'GET':
        is_active = cache.get(cache_key, True)  
        return Response({'is_active': is_active})


@api_view(['POST'])
def enroll(request):
    if request.method == 'POST':
        fingerprint_templates = JSONParser().parse(request)
        print(fingerprint_templates)
    return render(request, 'pages/test.html')
 
@api_view(['POST'])
def verify(request):
    if request.method == 'POST':
        match_id = JSONParser().parse(request)
        print(match_id)
    return render(request, 'pages/test.html')

