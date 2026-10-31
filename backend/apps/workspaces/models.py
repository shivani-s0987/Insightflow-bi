from django.conf import settings
from django.db import models
class Workspace(models.Model):
    name=models.CharField(max_length=120)
    slug=models.SlugField(max_length=140, unique=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='owned_workspaces')
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
class Membership(models.Model):
    class Role(models.TextChoices): OWNER='owner','Owner'; ADMIN='administrator','Administrator'; ANALYST='analyst','Analyst'; VIEWER='viewer','Viewer'
    workspace=models.ForeignKey(Workspace,on_delete=models.CASCADE,related_name='memberships')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='workspace_memberships')
    role=models.CharField(max_length=20,choices=Role.choices,default=Role.ANALYST)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['workspace','user'],name='unique_workspace_member')]
