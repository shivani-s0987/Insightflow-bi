from django.urls import path
from . import views
urlpatterns=[path('auth/csrf/',views.csrf),path('auth/register/',views.register),path('auth/login/',views.sign_in),path('auth/logout/',views.sign_out),path('auth/me/',views.me)]
