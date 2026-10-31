from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import apps.datasets.models
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),('workspaces','0001_initial')]
    operations=[migrations.CreateModel(name='Dataset',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=180)),('source_file',models.FileField(upload_to=apps.datasets.models.upload_path)),('file_format',models.CharField(max_length=8)),('status',models.CharField(choices=[('ready','Ready'),('failed','Failed'),('processing','Processing')],default='processing',max_length=20)),('row_count',models.PositiveBigIntegerField(default=0)),('column_count',models.PositiveIntegerField(default=0)),('columns',models.JSONField(default=list)),('pipeline',models.JSONField(default=list)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('created_by',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),('workspace',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='datasets',to='workspaces.workspace'))],options={'ordering':['-created_at']})]
