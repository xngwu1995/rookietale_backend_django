from pathlib import Path
import sys, os
from datetime import timedelta
from decouple import config

# AWS Credentials
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')

# Secret Key
SECRET_KEY = config('SECRET_KEY')

# Debug mode
DEBUG = config('DEBUG', default=False, cast=bool)

# CORS Settings
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS').split(',')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS').split(',')

# Cookie Settings
SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)

# Allowed Hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Internal IPs - Setting it to allow all IPs for development purposes
INTERNAL_IPS = config('INTERNAL_IPS', default='127.0.0.1').split(',')

# File Storage
DEFAULT_FILE_STORAGE = config('DEFAULT_FILE_STORAGE', default='storages.backends.s3boto3.S3Boto3Storage')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')

# API Keys
CHAT_GPT_API_KEY = config('CHAT_GPT_API_KEY')
EXPO_ACCESS_TOKEN = config('EXPO_ACCESS_TOKEN')
FINN_API_KEY = config('FINN_API_KEY')

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'TIMEOUT': 86400  # 1 day
    }
}

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
    }
}

# Testing Flag
TESTING = (" ".join(sys.argv)).find('manage.py test') != -1

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition

INSTALLED_APPS = [
    # django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.db.models.functions',

    # third party packages
    'rest_framework',
    "debug_toolbar",
    'django_filters',
    'notifications',
    'corsheaders',
    'django_celery_beat',

    # project apps
    'accounts',
    'chatgpt',
    'tweets',
    'friendships',
    'newsfeeds',
    'comments',
    'likes',
    'taskmanager',
    'stocks',
]

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_ALWAYS_EAGER = TESTING
CELERY_BEAT_SCHEDULER = config('CELERY_BEAT_SCHEDULER', default='django_celery_beat.schedulers:DatabaseScheduler')

if config('RUNNING_IN_AWS', default='False').lower() == 'true':
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'region': config('CELERY_BROKER_REGION', default='us-west-2'),
        'visibility_timeout': config('CELERY_BROKER_VISIBILITY_TIMEOUT', default=3600, cast=int),
        'polling_interval': config('CELERY_BROKER_POLLING_INTERVAL', default=20, cast=int),
    }
    CELERY_TASK_DEFAULT_QUEUE = config('CELERY_TASK_DEFAULT_QUEUE')
    CELERY_TASK_QUEUES = {
        'rookietale': {
            'url': config('CELERY_TASK_QUEUE_URL')
        },
    }
    INSTALLED_APPS += ['ebhealthcheck.apps.EBHealthCheckConfig']

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
       'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]


ROOT_URLCONF = 'twitter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'twitter.wsgi.application'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    # You can configure other settings here as needed
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760 # 10MB in bytes



TESTING = ((" ".join(sys.argv)).find('manage.py test') != -1)
if TESTING:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILE_DIRS = [os.path.join(BASE_DIR, "static"),]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = 'media/'
