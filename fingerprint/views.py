from django.shortcuts import render
from rest_framework.decorators import api_view

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status


def index(request):
    return render(request, 'pages/test.html')

def mode():
    pass

def is_fingerprint_active(request):
    pass

@api_view(['POST'])
def enroll(request):
    if request.method == 'POST':
        fingerprint_templates = JSONParser().parse(request)
        print(fingerprint_templates)
    return render(request, 'pages/test.html')

def verify_fingerprint(request):
    pass
