import io
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.datasets.models import Dataset
from apps.datasets.permissions import require_role
from apps.datasets.services import read_dataset,apply_pipeline
from .models import Report
@api_view(['GET','POST'])
def reports(request):
    if request.method=='GET':
        wid=request.query_params.get('workspace'); require_role(request.user,wid)
        return Response([{'id':r.id,'title':r.title,'dataset_id':r.dataset_id,'created_at':r.created_at} for r in Report.objects.filter(workspace_id=wid)])
    did=request.data.get('dataset_id'); d=get_object_or_404(Dataset,pk=did); require_role(request.user,d.workspace_id,write=True)
    title=str(request.data.get('title','')).strip() or f'{d.name} report'
    config=request.data.get('config',{})
    r=Report.objects.create(workspace=d.workspace,created_by=request.user,title=title[:180],dataset_id=d.id,config=config)
    return Response({'id':r.id,'title':r.title,'dataset_id':r.dataset_id,'created_at':r.created_at},status=201)
@api_view(['GET'])
def report_export(request,report_id):
    r=get_object_or_404(Report,pk=report_id); require_role(request.user,r.workspace_id); d=get_object_or_404(Dataset,pk=r.dataset_id,workspace_id=r.workspace_id); df=apply_pipeline(read_dataset(d),d.pipeline)
    out=io.BytesIO()
    safe=df.copy()
    for col in safe.select_dtypes(include=['object','string']).columns:
        safe[col]=safe[col].map(lambda v: "'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@','\t','\r')) else v)
    with pd.ExcelWriter(out,engine='openpyxl') as writer: safe.to_excel(writer,index=False,sheet_name='Data')
    response=HttpResponse(out.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'); response['Content-Disposition']=f'attachment; filename="report-{r.id}.xlsx"'; return response
