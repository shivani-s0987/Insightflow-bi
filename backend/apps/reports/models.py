from django.conf import settings
from django.db import models
from apps.workspaces.models import Workspace
class Report(models.Model):
    workspace=models.ForeignKey(Workspace,on_delete=models.CASCADE,related_name='reports')
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    title=models.CharField(max_length=180)
    dataset_id=models.PositiveIntegerField()
    config=models.JSONField(default=dict)
    created_at=models.DateTimeField(auto_now_add=True)
