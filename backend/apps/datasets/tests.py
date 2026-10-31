import io, tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from apps.workspaces.models import Workspace,Membership
from apps.datasets.models import Dataset
from apps.datasets.services import apply_pipeline
import pandas as pd
class PipelineTests(TestCase):
    def test_duplicate_removal_and_fill(self):
        df=pd.DataFrame({'value':[1,None,1],'name':[' A ','B',' A ']})
        out=apply_pipeline(df,[{'op':'fill_missing','column':'value','method':'constant','value':0},{'op':'trim_strings','column':'name'},{'op':'drop_duplicates'}])
        self.assertEqual(len(out),2); self.assertEqual(out['value'].isna().sum(),0); self.assertEqual(out.iloc[0]['name'],'A')
    def test_invalid_column_rejected(self):
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError): apply_pipeline(pd.DataFrame({'x':[1]}),[{'op':'drop_column','column':'secret'}])
class DatasetAPITests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username='analyst@example.com',email='analyst@example.com',password='Secure-password-123')
        self.ws=Workspace.objects.create(name='Private',slug='private-test',created_by=self.user); Membership.objects.create(workspace=self.ws,user=self.user,role='owner')
        self.client=APIClient(); self.client.force_authenticate(self.user)
    @override_settings(MEDIA_ROOT=tempfile.gettempdir()+'/insightflow-test-uploads')
    def test_csv_upload_and_profile(self):
        f=SimpleUploadedFile('sales.csv',b'category,revenue\nA,10\nB,20\nA,10\n',content_type='text/csv')
        r=self.client.post('/api/v1/datasets/upload/',{'workspace':self.ws.id,'file':f},format='multipart')
        self.assertEqual(r.status_code,201,r.data); did=r.data['id']
        p=self.client.get(f'/api/v1/datasets/{did}/profile/'); self.assertEqual(p.status_code,200); self.assertEqual(p.data['rows'],3); self.assertEqual(p.data['duplicate_rows'],1)
    def test_cross_workspace_denied(self):
        other=get_user_model().objects.create_user(username='other@example.com',password='Secure-password-456')
        ws2=Workspace.objects.create(name='Other',slug='other-test',created_by=other)
        from django.core.files.base import ContentFile
        d=Dataset.objects.create(workspace=ws2,created_by=other,name='Private',file_format='csv',status='ready'); d.source_file.save('p.csv',ContentFile(b'a\n1\n'))
        response=self.client.get(f'/api/v1/datasets/{d.id}/')
        self.assertEqual(response.status_code,404)

class AnalyticsAPITests(TestCase):
    def setUp(self):
        from django.core.files.base import ContentFile
        self.user=get_user_model().objects.create_user(username='bi@example.com',email='bi@example.com',password='Secure-password-789')
        self.ws=Workspace.objects.create(name='BI',slug='bi-test',created_by=self.user)
        Membership.objects.create(workspace=self.ws,user=self.user,role='analyst')
        self.dataset=Dataset.objects.create(workspace=self.ws,created_by=self.user,name='Orders',file_format='csv',status='ready')
        self.dataset.source_file.save('orders.csv',ContentFile(b'region,revenue\nEast,10\nWest,20\nEast,5\n'),save=True)
        self.client=APIClient(); self.client.force_authenticate(self.user)
    def test_grouped_sum_uses_uploaded_values(self):
        response=self.client.post('/api/v1/analytics/query/',{'dataset_id':self.dataset.id,'group_by':'region','metric':'revenue','aggregation':'sum'},format='json')
        self.assertEqual(response.status_code,200,response.data)
        values={row['label']:row['value'] for row in response.data['data']}
        self.assertEqual(values,{'East':15,'West':20})
    def test_unsupported_aggregation_is_rejected(self):
        response=self.client.post('/api/v1/analytics/query/',{'dataset_id':self.dataset.id,'aggregation':'exec'},format='json')
        self.assertEqual(response.status_code,400)
