from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),('workspaces','0001_initial')]
    operations=[migrations.CreateModel(name='AuditEvent',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('action',models.CharField(max_length=100)),('resource_type',models.CharField(max_length=80)),('resource_id',models.CharField(blank=True,max_length=80)),('created_at',models.DateTimeField(auto_now_add=True)),('actor',models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL)),('workspace',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='audit_events',to='workspaces.workspace'))],options={'ordering':['-created_at']})]
