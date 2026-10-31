from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.workspaces.models import Membership
class AuthenticationTests(TestCase):
    def setUp(self): self.client=APIClient()
    def test_registration_creates_owner_workspace_and_session(self):
        response=self.client.post('/api/v1/auth/register/',{'name':'Taylor Analyst','email':'taylor@example.com','password':'Distinct-Password-741!'},format='json')
        self.assertEqual(response.status_code,201,response.data)
        user=get_user_model().objects.get(email='taylor@example.com')
        membership=Membership.objects.get(user=user)
        self.assertEqual(membership.role,'owner')
        self.assertTrue(self.client.session.get('_auth_user_id'))
    def test_short_password_is_rejected(self):
        response=self.client.post('/api/v1/auth/register/',{'name':'Taylor','email':'taylor@example.com','password':'short'},format='json')
        self.assertEqual(response.status_code,400)
