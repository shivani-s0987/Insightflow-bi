from django.urls import path
from .views import query,insight_summary
from .demo_views import demo_overview
urlpatterns=[path('analytics/query/',query),path('analytics/summary/',insight_summary),path('demo/overview/',demo_overview)]
