from django.urls import path
from .views import reports,report_export
urlpatterns=[path('reports/',reports),path('reports/<int:report_id>/export.xlsx',report_export)]
