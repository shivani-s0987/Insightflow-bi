from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.middleware.csrf import get_token
from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from apps.workspaces.models import Workspace, Membership
User=get_user_model()
class AuthThrottle(AnonRateThrottle): rate='10/hour'
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf(request): return Response({'csrfToken':get_token(request)})
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def register(request):
    email=str(request.data.get('email','')).strip().lower(); password=str(request.data.get('password','')); name=str(request.data.get('name','')).strip()
    if not email or '@' not in email: return Response({'code':'invalid_email','detail':'Enter a valid email address.'},status=400)
    if len(password)<10: return Response({'code':'weak_password','detail':'Password must contain at least 10 characters.'},status=400)
    try: validate_password(password)
    except DjangoValidationError: return Response({'code':'weak_password','detail':'Choose a less common password that does not closely resemble your account details.'},status=400)
    if User.objects.filter(username=email).exists(): return Response({'code':'account_exists','detail':'An account with this email already exists.'},status=409)
    user=User.objects.create_user(username=email,email=email,password=password,first_name=name[:150])
    base=slugify(name or email.split('@')[0])[:100] or 'workspace'; slug=base; i=2
    while Workspace.objects.filter(slug=slug).exists(): slug=f'{base}-{i}'; i+=1
    ws=Workspace.objects.create(name=(name or 'My')+' Workspace',slug=slug,created_by=user)
    Membership.objects.create(workspace=ws,user=user,role=Membership.Role.OWNER)
    login(request,user); return Response({'user':{'id':user.id,'email':user.email,'name':user.first_name},'workspace':{'id':ws.id,'name':ws.name,'slug':ws.slug,'role':'owner'}},status=201)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def sign_in(request):
    email=str(request.data.get('email','')).strip().lower(); password=str(request.data.get('password',''))
    user=authenticate(request,username=email,password=password)
    if not user: return Response({'code':'invalid_credentials','detail':'Email or password is incorrect.'},status=400)
    login(request,user); return Response({'user':{'id':user.id,'email':user.email,'name':user.first_name}})
@api_view(['POST'])
def sign_out(request): logout(request); return Response({'status':'signed_out'})
@api_view(['GET'])
def me(request):
    user=request.user
    return Response({'user':{'id':user.id,'email':user.email,'name':user.first_name},'workspaces':[{'id':m.workspace_id,'name':m.workspace.name,'slug':m.workspace.slug,'role':m.role} for m in Membership.objects.filter(user=user).select_related('workspace')]})
