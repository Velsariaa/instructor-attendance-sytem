from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore # type: ignore
from django.conf import settings # type: ignore
from django.conf.urls.static import static # type: ignore
from django.contrib.auth import views as auth_views # type: ignore
from webapp.views import superuser_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('webapp.urls')),
    path('fingerprint/', include('fingerprint.urls')),
    path('login/', superuser_login, name='adminlogin'),
    path('user-login/', auth_views.LoginView.as_view(template_name='registration/user-login.html'), name='user-login'),
] +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)