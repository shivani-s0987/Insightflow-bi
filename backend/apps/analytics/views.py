import pandas as pd
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
class AnalyticsThrottle(UserRateThrottle): rate='60/minute'
from apps.datasets.models import Dataset
from apps.datasets.permissions import require_role
from apps.datasets.services import read_dataset, apply_pipeline, json_safe
AGG={'count','distinct_count','sum','mean','min','max','median'}
@api_view(['POST'])
@throttle_classes([AnalyticsThrottle])
def query(request):
    dataset_id=request.data.get('dataset_id')
    try: dataset_id=int(dataset_id)
    except (ValueError,TypeError): return Response({'detail':'dataset_id must be an integer.'},status=400)
    d=get_object_or_404(Dataset,pk=dataset_id); require_role(request.user,d.workspace_id)
    df=apply_pipeline(read_dataset(d),d.pipeline); group=request.data.get('group_by'); metric=request.data.get('metric'); agg=request.data.get('aggregation','count'); filters=request.data.get('filters',[]); raw_limit=request.data.get('limit',50)
    try: limit=min(max(int(raw_limit),1),500)
    except (ValueError,TypeError): return Response({'detail':'limit must be an integer between 1 and 500.'},status=400)
    if group is not None and not isinstance(group,str): return Response({'detail':'group_by must be a column name or null.'},status=400)
    if metric is not None and not isinstance(metric,str): return Response({'detail':'metric must be a column name or null.'},status=400)
    if not isinstance(filters,list) or len(filters)>20 or any(not isinstance(f,dict) for f in filters): return Response({'detail':'filters must be a list of at most 20 filter objects.'},status=400)
    if agg not in AGG: return Response({'detail':'Unsupported aggregation.'},status=400)
    for f in filters:
        col=f.get('column'); op=f.get('op'); val=f.get('value')
        if not isinstance(col,str) or col not in df.columns: return Response({'detail':'Filter references an unknown column.'},status=400)
        if op=='eq': df=df[df[col].astype(str)==str(val)]
        elif op=='ne': df=df[df[col].astype(str)!=str(val)]
        elif op=='contains':
            if len(str(val))>100: return Response({'detail':'Contains filter is too long.'},status=400)
            df=df[df[col].astype('string').str.contains(str(val),case=False,na=False,regex=False)]
        elif op in ('gt','gte','lt','lte'):
            s=pd.to_numeric(df[col],errors='coerce')
            try: n=float(val)
            except (ValueError,TypeError): return Response({'detail':'Numeric filter value is invalid.'},status=400)
            df=df[{'gt':s>n,'gte':s>=n,'lt':s<n,'lte':s<=n}[op]]
        else: return Response({'detail':'Unsupported filter operation.'},status=400)
    if group and group not in df.columns: return Response({'detail':'Unknown grouping column.'},status=400)
    if agg not in ('count','distinct_count') and (metric not in df.columns or not pd.api.types.is_numeric_dtype(df[metric])): return Response({'detail':'This aggregation requires a numeric metric column.'},status=400)
    if agg=='count':
        result=df.groupby(group,dropna=False).size().reset_index(name='value') if group else pd.DataFrame({'label':['All records'],'value':[len(df)]})
    elif agg=='distinct_count':
        if not metric or metric not in df.columns: return Response({'detail':'distinct_count requires a valid metric column.'},status=400)
        result=df.groupby(group,dropna=False)[metric].nunique().reset_index(name='value') if group else pd.DataFrame({'label':['All records'],'value':[df[metric].nunique()]})
    else:
        result=df.groupby(group,dropna=False)[metric].agg(agg).reset_index(name='value') if group else pd.DataFrame({'label':['All records'],'value':[getattr(df[metric],agg)()]})
    if group: result=result.rename(columns={group:'label'})
    result=result.sort_values('value',ascending=False,kind='stable').head(limit)
    data=[{'label':json_safe(r['label']),'value':json_safe(r['value'])} for r in result.to_dict(orient='records')]
    return Response({'dataset_id':d.id,'dataset_name':d.name,'row_count':len(df),'group_by':group,'metric':metric,'aggregation':agg,'data':data})
@api_view(['GET'])
def insight_summary(request):
    workspace_id=request.query_params.get('workspace'); require_role(request.user,workspace_id)
    datasets=Dataset.objects.filter(workspace_id=workspace_id,status='ready')
    return Response({'dataset_count':datasets.count(),'rows_total':sum(d.row_count for d in datasets),'latest_dataset':datasets.first().name if datasets.exists() else None,'datasets':[{'id':d.id,'name':d.name,'rows':d.row_count,'columns':d.column_count} for d in datasets[:10]]})
