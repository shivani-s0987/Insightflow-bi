import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'local-only-change-me-before-deployment')
DEBUG = os.getenv('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',') if h.strip()]
INSTALLED_APPS = [
 'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
 'rest_framework','corsheaders','apps.accounts','apps.workspaces','apps.datasets','apps.analytics','apps.dashboards','apps.reports','apps.audit',
]
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','corsheaders.middleware.CorsMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
if os.getenv('DATABASE_URL','').startswith('postgres://') or os.getenv('DATABASE_URL','').startswith('postgresql://'):
    import urllib.parse
    u=urllib.parse.urlparse(os.environ['DATABASE_URL'])
    DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':u.path.lstrip('/'),'USER':u.username,'PASSWORD':u.password,'HOST':u.hostname,'PORT':u.port or 5432,'CONN_MAX_AGE':60}}
else:
    DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':os.getenv('SQLITE_PATH', str(BASE_DIR/'db.sqlite3')),'OPTIONS':{'timeout':20}}}
AUTH_PASSWORD_VALIDATORS = [{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':10}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'; TIME_ZONE='Asia/Kolkata'; USE_I18N=True; USE_TZ=True
STATIC_URL='static/'; STATIC_ROOT=BASE_DIR/'staticfiles'; MEDIA_ROOT=Path(os.getenv('MEDIA_ROOT',str(BASE_DIR/'private_uploads'))); MEDIA_URL='/media/'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated'],'DEFAULT_THROTTLE_CLASSES':['rest_framework.throttling.AnonRateThrottle','rest_framework.throttling.UserRateThrottle'],'DEFAULT_THROTTLE_RATES':{'anon':'20/hour','user':'120/minute','upload':'10/hour','analytics':'60/minute'},'DEFAULT_RENDERER_CLASSES':['rest_framework.renderers.JSONRenderer'] if not DEBUG else ['rest_framework.renderers.JSONRenderer','rest_framework.renderers.BrowsableAPIRenderer']}
CORS_ALLOWED_ORIGINS=[x.strip() for x in os.getenv('CORS_ALLOWED_ORIGINS','http://localhost:5173').split(',') if x.strip()]
CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.getenv('CSRF_TRUSTED_ORIGINS','http://localhost:5173').split(',') if x.strip()]
SESSION_COOKIE_HTTPONLY=True; CSRF_COOKIE_HTTPONLY=False; SESSION_COOKIE_SECURE=not DEBUG; CSRF_COOKIE_SECURE=not DEBUG; SECURE_CONTENT_TYPE_NOSNIFF=True; X_FRAME_OPTIONS='DENY'; SECURE_REFERRER_POLICY='same-origin'
FILE_UPLOAD_MAX_MEMORY_SIZE=2*1024*1024; DATA_UPLOAD_MAX_MEMORY_SIZE=15*1024*1024; MAX_UPLOAD_BYTES=int(os.getenv('MAX_UPLOAD_BYTES', '10485760'))
