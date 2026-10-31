import json
from pathlib import Path
import pandas as pd
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, throttle_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import ValidationError
from .models import Dataset
from .services import read_dataset, apply_pipeline, json_safe, ALLOWED_EXT
from .permissions import require_role
class UploadThrottle(UserRateThrottle): rate='10/hour'
def get_df(dataset): return apply_pipeline(read_dataset(dataset),dataset.pipeline)
@api_view(['GET','POST'])
def dataset_collection(request):
    if request.method=='GET':
        workspace_id=request.query_params.get('workspace')
        if not workspace_id: return Response({'detail':'workspace query parameter is required.'},status=400)
        require_role(request.user,workspace_id)
        qs=Dataset.objects.filter(workspace_id=workspace_id,status='ready').select_related('created_by')
        return Response([{'id':d.id,'name':d.name,'format':d.file_format,'rows':d.row_count,'columns':d.column_count,'column_names':d.columns,'created_at':d.created_at,'updated_at':d.updated_at} for d in qs])
    return Response({'detail':'Use the upload endpoint.'},status=405)
@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser])
@throttle_classes([UploadThrottle])
def upload_dataset(request):
    workspace_id=request.data.get('workspace'); m=require_role(request.user,workspace_id,write=True)
    f=request.FILES.get('file')
    if not f: return Response({'detail':'Choose a CSV or Excel file.'},status=400)
    ext=Path(f.name).suffix.lower()
    if ext not in ALLOWED_EXT: return Response({'detail':'Supported formats are CSV and XLSX; legacy XLS is not enabled.'},status=415)
    if f.size>settings.MAX_UPLOAD_BYTES: return Response({'detail':f'File exceeds the {settings.MAX_UPLOAD_BYTES//1024//1024} MB upload limit.'},status=413)
    if f.size==0: return Response({'detail':'The selected file is empty.'},status=400)
    fmt='csv' if ext=='.csv' else ('xlsx' if ext=='.xlsx' else 'xls')
    d=Dataset(workspace=m.workspace,created_by=request.user,name=str(request.data.get('name') or Path(f.name).stem)[:180],file_format=fmt)
    d.source_file.save(f.name,f,save=False)
    try:
        # Content sniffing: CSV must decode as text; XLSX is a ZIP-based OOXML container.
        with d.source_file.open('rb') as stream: header=stream.read(8)
        if fmt=='xlsx' and not header.startswith(b'PK'): raise ValidationError({'detail':'The file extension does not match a valid XLSX workbook.'})
        if fmt=='csv' and b'\x00' in header: raise ValidationError({'detail':'The file does not appear to be a text CSV.'})
        d.save(); df=read_dataset(d)
        if df.empty and len(df.columns)==0: raise ValidationError({'detail':'No tabular data was found.'})
        d.row_count=len(df); d.column_count=len(df.columns); d.columns=[{'name':str(c),'dtype':str(df[c].dtype)} for c in df.columns]; d.status='ready'; d.save(update_fields=['row_count','column_count','columns','status','updated_at'])
    except Exception:
        if d.pk: d.source_file.delete(save=False); d.delete()
        else: d.source_file.delete(save=False)
        raise
    return Response({'id':d.id,'name':d.name,'format':d.file_format,'rows':d.row_count,'columns':d.column_count,'column_names':d.columns,'status':d.status},status=201)
@api_view(['GET','DELETE'])
def dataset_detail(request,dataset_id):
    d=get_object_or_404(Dataset.objects.select_related('workspace'),pk=dataset_id); require_role(request.user,d.workspace_id,write=request.method=='DELETE')
    if request.method=='DELETE': d.source_file.delete(save=False); d.delete(); return Response(status=204)
    return Response({'id':d.id,'name':d.name,'format':d.file_format,'rows':d.row_count,'columns':d.column_count,'column_names':d.columns,'pipeline':d.pipeline,'created_at':d.created_at})
@api_view(['GET'])
def dataset_preview(request,dataset_id):
    d=get_object_or_404(Dataset,pk=dataset_id); require_role(request.user,d.workspace_id)
    try: limit=min(max(int(request.query_params.get('limit',50)),1),200); offset=max(int(request.query_params.get('offset',0)),0)
    except ValueError: return Response({'detail':'limit and offset must be integers.'},status=400)
    df=get_df(d); rows=[{str(k):json_safe(v) for k,v in r.items()} for r in df.iloc[offset:offset+limit].to_dict(orient='records')]
    return Response({'columns':[{'name':str(c),'dtype':str(df[c].dtype)} for c in df.columns],'rows':rows,'total':len(df),'limit':limit,'offset':offset})
@api_view(['GET'])
def dataset_profile(request,dataset_id):
    d=get_object_or_404(Dataset,pk=dataset_id); require_role(request.user,d.workspace_id); df=get_df(d)
    cols=[]
    for c in df.columns:
        s=df[c]; numeric=pd.to_numeric(s,errors='coerce'); is_num=pd.api.types.is_numeric_dtype(s)
        item={'name':str(c),'dtype':str(s.dtype),'missing':int(s.isna().sum()),'missing_percent':round(float(s.isna().mean()*100),2) if len(s) else 0,'unique':int(s.nunique(dropna=True)),'constant':bool(s.nunique(dropna=True)<=1),'sample': [json_safe(v) for v in s.dropna().head(3).tolist()]}
        if is_num:
            clean=numeric.dropna(); item['statistics']={'min':json_safe(clean.min()) if len(clean) else None,'max':json_safe(clean.max()) if len(clean) else None,'mean':json_safe(clean.mean()) if len(clean) else None,'median':json_safe(clean.median()) if len(clean) else None,'std':json_safe(clean.std()) if len(clean)>1 else None,'p25':json_safe(clean.quantile(.25)) if len(clean) else None,'p75':json_safe(clean.quantile(.75)) if len(clean) else None}
        elif pd.api.types.is_datetime64_any_dtype(s): item['statistics']={'min':json_safe(s.min()),'max':json_safe(s.max())}
        else: item['top_values']=[{'value':json_safe(k),'count':int(v)} for k,v in s.value_counts(dropna=True).head(8).items()]
        cols.append(item)
    duplicate_count=int(df.duplicated().sum()); missing_cells=int(df.isna().sum().sum()); total_cells=df.size
    score=100 if total_cells==0 else round(100*(1-missing_cells/total_cells)* (1-duplicate_count/max(len(df),1)),1)
    return Response({'dataset_id':d.id,'rows':len(df),'columns':len(df.columns),'duplicate_rows':duplicate_count,'missing_cells':missing_cells,'quality_score':max(0,score),'columns_profile':cols,'warnings':[f'{c}: {int(df[c].isna().sum())} missing values' for c in df if df[c].isna().any()]})
@api_view(['POST'])
def transform_dataset(request,dataset_id):
    d=get_object_or_404(Dataset,pk=dataset_id); require_role(request.user,d.workspace_id,write=True)
    steps=request.data.get('pipeline')
    if not isinstance(steps,list): return Response({'detail':'pipeline must be a list of transformation steps.'},status=400)
    df=apply_pipeline(read_dataset(d),steps)
    return Response({'preview_rows':[{str(k):json_safe(v) for k,v in r.items()} for r in df.head(50).to_dict(orient='records')],'rows':len(df),'columns':[{'name':str(c),'dtype':str(df[c].dtype)} for c in df.columns],'pipeline':steps})
@api_view(['POST'])
def save_pipeline(request,dataset_id):
    d=get_object_or_404(Dataset,pk=dataset_id); require_role(request.user,d.workspace_id,write=True); steps=request.data.get('pipeline')
    if not isinstance(steps,list): return Response({'detail':'pipeline must be a list.'},status=400)
    df=apply_pipeline(read_dataset(d),steps); d.pipeline=steps; d.row_count=len(df); d.column_count=len(df.columns); d.columns=[{'name':str(c),'dtype':str(df[c].dtype)} for c in df.columns]; d.save(update_fields=['pipeline','row_count','column_count','columns','updated_at'])
    return Response({'status':'saved','rows':len(df),'columns':d.columns,'pipeline':d.pipeline})
@api_view(['GET'])
def export_dataset(request,dataset_id):
    d=get_object_or_404(Dataset,pk=dataset_id); require_role(request.user,d.workspace_id); df=get_df(d)
    out=HttpResponse(content_type='text/csv; charset=utf-8'); out['Content-Disposition']=f'attachment; filename="dataset-{d.id}-processed.csv"'
    safe=df.copy()
    for col in safe.select_dtypes(include=['object','string']).columns:
        safe[col]=safe[col].map(lambda v: "'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@','\t','\r')) else v)
    safe.to_csv(out,index=False); return out
