from django.shortcuts import render

def index(request):
    return render(request, 'pages/test.html')

def mode():
    pass

def is_fingerprint_active():
    pass

def enroll_fingerprint():
    pass

def verify_fingerprint():
    pass
