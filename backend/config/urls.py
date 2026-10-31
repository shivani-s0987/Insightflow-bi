from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.http import require_GET
@require_GET
def health(request): return JsonResponse({'status':'ok','service':'insightflow-api'})
urlpatterns=[path('admin/',admin.site.urls),path('api/v1/',include('apps.accounts.urls')),path('api/v1/',include('apps.workspaces.urls')),path('api/v1/',include('apps.datasets.urls')),path('api/v1/',include('apps.analytics.urls')),path('api/v1/',include('apps.dashboards.urls')),path('api/v1/',include('apps.reports.urls')),path('health/',health)]
