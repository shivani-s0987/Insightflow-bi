from django.conf import settings
from django.db import models
from apps.workspaces.models import Workspace
class Dashboard(models.Model):
    workspace=models.ForeignKey(Workspace,on_delete=models.CASCADE,related_name='dashboards')
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    name=models.CharField(max_length=180)
    description=models.TextField(blank=True)
    config=models.JSONField(default=dict)
    is_demo=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-updated_at']
