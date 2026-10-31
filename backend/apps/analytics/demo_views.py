import pandas as pd
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.workspaces.models import Workspace
from apps.datasets.models import Dataset
from apps.datasets.services import read_dataset, apply_pipeline, json_safe
@api_view(['GET'])
@permission_classes([AllowAny])
def demo_overview(request):
    """Read-only, explicitly synthetic demo data; never accepts an arbitrary workspace ID."""
    ws=Workspace.objects.filter(slug='insightflow-demo').first()
    if not ws: return Response({'available':False,'message':'Run the seed_demo command to populate the demo workspace.'})
    ds=Dataset.objects.filter(workspace=ws,name='E-commerce Orders',status='ready').first()
    if not ds: return Response({'available':False,'message':'Demo data is not seeded yet.'})
    df=apply_pipeline(read_dataset(ds),ds.pipeline)
    sales_df=df[df['status'].astype(str).str.lower()=='completed'].copy() if 'status' in df else df.copy()
    revenue=pd.to_numeric(sales_df['revenue'],errors='coerce') if 'revenue' in sales_df else pd.Series(dtype=float)
    monthly=[]; categories=[]
    if 'order_date' in sales_df and 'revenue' in sales_df:
        work=sales_df.copy(); work['_date']=pd.to_datetime(work['order_date'],errors='coerce'); work['_month']=work['_date'].dt.to_period('M').astype('string')
        g=work.groupby('_month',dropna=True)['revenue'].sum().sort_index().tail(12)
        monthly=[{'month':str(k),'value':json_safe(v)} for k,v in g.items()]
    if 'category' in sales_df and 'revenue' in sales_df:
        g=sales_df.groupby('category')['revenue'].sum().sort_values(ascending=False)
        categories=[{'label':str(k),'value':json_safe(v)} for k,v in g.items()]
    total=float(revenue.sum()) if len(revenue) else 0
    return Response({'available':True,'dataset_name':ds.name,'rows':len(df),'total_revenue':round(total,2),'average_order_value':round(total/len(sales_df),2) if len(sales_df) else 0,'completed_orders':len(sales_df),'revenue_scope':'Completed orders only','monthly_revenue':monthly,'revenue_by_category':categories})
