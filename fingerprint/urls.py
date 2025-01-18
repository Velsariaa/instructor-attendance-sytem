from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mode', views.mode, name='mode'),
    path('is_active', views.is_active, name='is_active'),
    path('enroll', views.enroll, name='enroll'),
    path('verify', views.verify, name='verify'),
]