import uuid
from django.conf import settings
from django.db import models
from apps.workspaces.models import Workspace

def upload_path(instance, filename): return f'workspace_{instance.workspace_id}/{uuid.uuid4().hex}.data'
class Dataset(models.Model):
    class Status(models.TextChoices): READY='ready','Ready'; FAILED='failed','Failed'; PROCESSING='processing','Processing'
    workspace=models.ForeignKey(Workspace,on_delete=models.CASCADE,related_name='datasets')
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    name=models.CharField(max_length=180)
    source_file=models.FileField(upload_to=upload_path)
    file_format=models.CharField(max_length=8)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.PROCESSING)
    row_count=models.PositiveBigIntegerField(default=0)
    column_count=models.PositiveIntegerField(default=0)
    columns=models.JSONField(default=list)
    pipeline=models.JSONField(default=list)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']
