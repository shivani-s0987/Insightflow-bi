from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.datasets.permissions import require_role
from .models import Dashboard
@api_view(['GET','POST'])
def dashboards(request):
    if request.method=='GET':
        wid=request.query_params.get('workspace'); require_role(request.user,wid)
        return Response([{'id':d.id,'name':d.name,'description':d.description,'config':d.config,'is_demo':d.is_demo,'updated_at':d.updated_at} for d in Dashboard.objects.filter(workspace_id=wid)])
    wid=request.data.get('workspace_id'); require_role(request.user,wid,write=True); name=str(request.data.get('name','')).strip()
    if not name: return Response({'detail':'Dashboard name is required.'},status=400)
    config=request.data.get('config',{})
    if not isinstance(config,dict): return Response({'detail':'config must be an object.'},status=400)
    d=Dashboard.objects.create(workspace_id=wid,created_by=request.user,name=name[:180],description=str(request.data.get('description',''))[:2000],config=config)
    return Response({'id':d.id,'name':d.name,'description':d.description,'config':d.config,'updated_at':d.updated_at},status=201)
@api_view(['GET','PATCH','DELETE'])
def dashboard_detail(request,dashboard_id):
    d=get_object_or_404(Dashboard,pk=dashboard_id); require_role(request.user,d.workspace_id,write=request.method in ('PATCH','DELETE'))
    if request.method=='GET': return Response({'id':d.id,'name':d.name,'description':d.description,'config':d.config,'updated_at':d.updated_at})
    if request.method=='DELETE': d.delete(); return Response(status=204)
    if 'name' in request.data: d.name=str(request.data['name']).strip()[:180] or d.name
    if 'description' in request.data: d.description=str(request.data['description'])[:2000]
    if 'config' in request.data:
        if not isinstance(request.data['config'],dict): return Response({'detail':'config must be an object.'},status=400)
        d.config=request.data['config']
    d.save(); return Response({'id':d.id,'name':d.name,'description':d.description,'config':d.config,'updated_at':d.updated_at})
