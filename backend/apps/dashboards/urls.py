from django.urls import path
from .views import dashboards,dashboard_detail
urlpatterns=[path('dashboards/',dashboards),path('dashboards/<int:dashboard_id>/',dashboard_detail)]
