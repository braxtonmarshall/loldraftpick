import os
from kombu import Queue
from dotenv import load_dotenv

load_dotenv()
# BROKER CONFIGURATION
BROKER_USER = os.getenv("BROKER_USER")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")
BROKER_HOST = os.getenv("BROKER_HOST")
BROKER_PORT = os.getenv("BROKER_PORT")
BROKER_VHOST = os.getenv("BROKER_VHOST")
# CELERY CONFIGURATION
CELERY_BROKER_URL = f'amqp://{BROKER_USER}:{BROKER_PASSWORD}@{BROKER_HOST}/{BROKER_VHOST}'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_ALWAYS_EAGER = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'EST'
CELERY_RESULT_CHORD_JOIN_TIMEOUT = 60
CELERY_TASK_QUEUES = [
    Queue('loldraft'),
    Queue('loldraft_api'),
    Queue('loldraft_token', max_length=2),
    Queue('loldraft_calcs')
]
CELERY_BEAT_SCHEDULE = {
    'token': {
        'task': 'loldraft.celery.token',
        'schedule': 1.25,
    }
}
CELERY_TASK_ROUTES = {
    'loldraft.celery.token': {'queue': 'loldraft_token'},
    'draftapp.tasks.parse*': {'queue': 'loldraft'},
    'draftapp.tasks.update*': {'queue': 'loldraft'},
    'draftapp.tasks.create*': {'queue': 'loldraft'},
    'draftapp.tasks.collect*': {'queue': 'loldraft'},
    'draftapp.tasks.fetch*': {'queue': 'loldraft_api'},
    'draftapp.tasks.query*': {'queue': 'loldraft'},
    'draftapp.tasks.process*': {'queue': 'loldraft'},
    'draftapp.tasks.save*': {'queue': 'loldraft'},
    'draftapp.tasks.calc*': {'queue': 'loldraft_calcs'},
}
# DJANGO CONFIGURATION
ALLOWED_HOSTS = [
    'www.loldraftpick.com', 'loldraftpick.com', '134.209.116.151', 'localhost'
]
#ADMINS = (
#    ('Braxton Marshall', os.getenv("ADMIN_EMAIL"))
#)
ADMIN_ENABLED = False
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache_bans'
    },
    'DMDIV': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache_bans/diamond'
    },
    'DMDII': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache_bans/diamond'
    },
    'MR': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache_bans/master'
    },
    'GMR': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache_bans/grandmaster'
    },
    'CHR': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache_bans/challenger'
    },
}
CSRF_COOKIE_SECURE = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'CONN_MAX_AGE': 0,
        'OPTIONS': {
            'read_default_file': '/home/mars/mysql/my.cnf',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
        'TEST': {
            'NAME': 'test_loldraft',
        },
    }
}
DEBUG = False
DEFAULT_FROM_EMAIL = os.getenv("ADMIN_EMAIL")
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'draftapp.apps.DraftappConfig',
    'django_celery_results',
]
INTERNAL_IPS = [
    '127.0.0.1',
]
LANGUAGE_CODE = 'en-us'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]
ROOT_URLCONF = 'loldraft.urls'
SECRET_KEY = os.getenv("SECRET_KEY")
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 1800
SECURE_SSL_REDIRECT = True
#SERVER_EMAIL = os.getenv("ADMIN_EMAIL")
SESSION_COOKIE_SECURE = True
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/loldraft/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
TIME_ZONE = 'EST'
USE_I18N = True
USE_L10N = True
USE_TZ = True
WSGI_APPLICATION = 'loldraft.wsgi.application'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
IMAGE_ROOT = os.path.join(BASE_DIR, 'static/img/')
#MEDIA_ROOT = os.path.join(BASE_DIR, 'draftapp/static/img/')
