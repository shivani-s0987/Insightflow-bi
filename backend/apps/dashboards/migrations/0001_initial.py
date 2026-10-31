from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),('workspaces','0001_initial')]
    operations=[migrations.CreateModel(name='Dashboard',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=180)),('description',models.TextField(blank=True)),('config',models.JSONField(default=dict)),('is_demo',models.BooleanField(default=False)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('created_by',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),('workspace',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='dashboards',to='workspaces.workspace'))],options={'ordering':['-updated_at']})]
