from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name='Workspace',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=120)),('slug',models.SlugField(max_length=140,unique=True)),('created_at',models.DateTimeField(auto_now_add=True)),('created_by',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='owned_workspaces',to=settings.AUTH_USER_MODEL))]),
        migrations.CreateModel(name='Membership',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('role',models.CharField(choices=[('owner','Owner'),('administrator','Administrator'),('analyst','Analyst'),('viewer','Viewer')],default='analyst',max_length=20)),('created_at',models.DateTimeField(auto_now_add=True)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='workspace_memberships',to=settings.AUTH_USER_MODEL)),('workspace',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='memberships',to='workspaces.workspace'))]),
        migrations.AddConstraint(model_name='membership',constraint=models.UniqueConstraint(fields=('workspace','user'),name='unique_workspace_member')),
    ]
