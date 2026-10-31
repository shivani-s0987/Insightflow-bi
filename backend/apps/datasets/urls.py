from django.urls import path
from . import views
urlpatterns=[path('datasets/',views.dataset_collection),path('datasets/upload/',views.upload_dataset),path('datasets/<int:dataset_id>/',views.dataset_detail),path('datasets/<int:dataset_id>/preview/',views.dataset_preview),path('datasets/<int:dataset_id>/profile/',views.dataset_profile),path('datasets/<int:dataset_id>/transform/preview/',views.transform_dataset),path('datasets/<int:dataset_id>/transform/save/',views.save_pipeline),path('datasets/<int:dataset_id>/export.csv',views.export_dataset)]
