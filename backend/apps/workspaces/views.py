from django.utils.text import slugify
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Workspace, Membership
@api_view(['GET','POST'])
def workspaces(request):
    if request.method=='GET':
        ms=Membership.objects.filter(user=request.user).select_related('workspace')
        return Response([{'id':m.workspace.id,'name':m.workspace.name,'slug':m.workspace.slug,'role':m.role} for m in ms])
    name=str(request.data.get('name','')).strip()
    if not name: return Response({'detail':'Workspace name is required.'},status=400)
    base=slugify(name)[:100] or 'workspace'; slug=base; i=2
    while Workspace.objects.filter(slug=slug).exists(): slug=f'{base}-{i}'; i+=1
    ws=Workspace.objects.create(name=name[:120],slug=slug,created_by=request.user); Membership.objects.create(workspace=ws,user=request.user,role='owner')
    return Response({'id':ws.id,'name':ws.name,'slug':ws.slug,'role':'owner'},status=201)
