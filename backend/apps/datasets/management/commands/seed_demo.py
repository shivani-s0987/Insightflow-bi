import io, csv, random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.text import slugify
from apps.workspaces.models import Workspace,Membership
from apps.datasets.models import Dataset
from apps.datasets.services import read_dataset
from apps.dashboards.models import Dashboard
from apps.reports.models import Report
class Command(BaseCommand):
    help='Create deterministic synthetic InsightFlow demo datasets, workspace, dashboard, and report. Safe to rerun.'
    def add_arguments(self,parser): parser.add_argument('--reset',action='store_true',help='Reset only the dedicated insightflow-demo workspace.')
    def handle(self,*args,**opts):
        User=get_user_model(); email='demo@insightflow.local'; user=User.objects.filter(username=email).first()
        if not user:
            user=User.objects.create_user(username=email,email=email,password='InsightFlow-Demo-2026!',first_name='Demo Analyst')
        ws=Workspace.objects.filter(slug='insightflow-demo').first()
        if ws and opts['reset']:
            for dataset in Dataset.objects.filter(workspace=ws): dataset.source_file.delete(save=False)
            ws.delete(); ws=None
        if not ws: ws=Workspace.objects.create(name='InsightFlow Demo',slug='insightflow-demo',created_by=user)
        Membership.objects.get_or_create(workspace=ws,user=user,defaults={'role':'owner'})
        if Dataset.objects.filter(workspace=ws).exists():
            self.stdout.write(self.style.WARNING('Demo datasets already exist; use --reset to recreate this demo workspace.')); return
        rng=random.Random(41026); products=['Accessories','Home','Electronics','Fitness','Apparel']; regions=['North','South','East','West','Central']
        def make_csv(name, headers, rows):
            s=io.StringIO(); w=csv.writer(s); w.writerow(headers); w.writerows(rows); return s.getvalue().encode()
        sales=[]; campaigns=[]; support=[]; start=date(2025,1,1)
        for i in range(1200):
            day=start+timedelta(days=rng.randrange(630)); qty=rng.randint(1,5); price=round(rng.uniform(18,450),2)
            sales.append([f'ORD-{i+1:05}',day.isoformat(),f'CUST-{rng.randrange(1,360):04}',rng.choice(products),rng.choice(regions),qty,price,round(qty*price,2),rng.choice(['completed','completed','completed','returned','pending'])])
        for i in range(240):
            day=start+timedelta(days=rng.randrange(630)); spend=round(rng.uniform(100,5000),2); clicks=rng.randint(80,2500); conversions=rng.randint(0,max(1,clicks//10))
            campaigns.append([f'CAMP-{i+1:04}',day.isoformat(),rng.choice(['Search','Social','Email','Display']),rng.choice(regions),spend,clicks,conversions,round(spend/max(conversions,1),2)])
        for i in range(600):
            day=start+timedelta(days=rng.randrange(630)); mins=max(1,round(rng.gauss(42,18),1))
            support.append([f'TKT-{i+1:05}',day.isoformat(),rng.choice(['Billing','Technical','Delivery','Returns','Account']),rng.choice(['Email','Chat','Phone']),rng.choice(['Low','Medium','High','Urgent']),mins,rng.choice(['Resolved','Resolved','Resolved','Escalated','Open']),rng.randint(1,5)])
        specs=[('E-commerce Orders','sales.csv',['order_id','order_date','customer_id','category','region','quantity','unit_price','revenue','status'],sales),('Marketing Performance','campaigns.csv',['campaign_id','date','channel','region','spend','clicks','conversions','cost_per_conversion'],campaigns),('Customer Support Operations','support.csv',['ticket_id','date','issue_type','channel','priority','resolution_minutes','status','satisfaction'],support)]
        for name,filename,headers,rows in specs:
            d=Dataset(workspace=ws,created_by=user,name=name,file_format='csv',status='processing'); d.source_file.save(filename,ContentFile(make_csv(name,headers,rows)),save=False); d.save(); df=read_dataset(d); d.row_count=len(df); d.column_count=len(df.columns); d.columns=[{'name':str(c),'dtype':str(df[c].dtype)} for c in df.columns]; d.status='ready'; d.save()
        sales_ds=Dataset.objects.get(workspace=ws,name='E-commerce Orders')
        Dashboard.objects.create(workspace=ws,created_by=user,name='Sales performance overview',description='Explore order volume, revenue, and category mix from the seeded orders dataset.',is_demo=True,config={'dataset_id':sales_ds.id,'charts':[{'title':'Revenue by category','group_by':'category','metric':'revenue','aggregation':'sum','type':'bar'},{'title':'Orders by region','group_by':'region','aggregation':'count','type':'donut'},{'title':'Revenue by date','group_by':'order_date','metric':'revenue','aggregation':'sum','type':'line'}]})
        Report.objects.create(workspace=ws,created_by=user,title='E-commerce data overview',dataset_id=sales_ds.id,config={'description':'Synthetic demo dataset report'})
        self.stdout.write(self.style.SUCCESS('Demo workspace seeded with 3 datasets, 2,040 rows, a dashboard, and a saved report.'))
        self.stdout.write('Development login: demo@insightflow.local / InsightFlow-Demo-2026!')
