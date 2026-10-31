from django.conf import settings
from django.db import models
from apps.workspaces.models import Workspace
class AuditEvent(models.Model):
    workspace=models.ForeignKey(Workspace,on_delete=models.CASCADE,related_name='audit_events')
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    action=models.CharField(max_length=100)
    resource_type=models.CharField(max_length=80)
    resource_id=models.CharField(max_length=80,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
