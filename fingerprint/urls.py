from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mode', views.mode, name='mode'),
    path('is_fingerprint_active', views.is_fingerprint_active, name='is_fingerprint_active'),
    path('enroll', views.enroll, name='enroll'),
    path('verify_fingerprint', views.verify_fingerprint, name='verify_fingerprint'),
]