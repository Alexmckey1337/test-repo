from __future__ import unicode_literals

"""
Django settings for edem project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import environ

from account.utils import create_token

BASE_DIR = environ.Path(__file__) - 2

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4y6l3@a0%vq394z6+w)k3-wl459r++v=z!jv1gw4+nt0sd5z+s'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = False
# DEBUG = True
ALLOWED_HOSTS = ['vocrm.org']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'rest_framework',
    # 'rest_framework.authtoken',
    'djcelery',

    'rest_auth',
    'corsheaders',
    # 'rest_auth.registration',

    'main',
    'account',
    'hierarchy',
    'notification',
    'event',
    'report',
    'status',
    'navigation',
    'partnership',
    'tv_crm',
    'summit',
    'location',
    #    'axes',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
 #   'axes.middleware.FailedLoginMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'edem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.path('templates')), ],
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

WSGI_APPLICATION = 'edem.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'crm',
        'USER': 'crmuse',
        'PASSWORD': '123456',
        'OPTIONS': {
            "init_command": "SET storage_engine=MYISAM",
            # "init_command": "SET default_storage_engine=MYISAM",
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = 'ru-RU'
USE_I18N = True
SITE_ID = 1
TIME_ZONE = 'Europe/Kiev'
USE_L10N = False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
MEDIA_ROOT = str(BASE_DIR.path('media'))
MEDIA_URL = '/media/'
STATIC_ROOT = str(BASE_DIR.path('static'))
# STATICFILES_DIRS = (str(BASE_DIR.path('static')),)
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

AUTHENTICATION_BACKENDS = (
    'account.auth_backends.CustomUserModelBackend',
)

CUSTOM_USER_MODEL = 'account.CustomUser'
DATE_FORMAT = 'd.m.Y'
DATETIME_FORMAT = 'd.m.Y H:i:s'
TIME_FORMAT = 'H:i:s'
SHORT_DATE_FORMAT = 'd.m.Y'

REST_AUTH_TOKEN_CREATOR = create_token
REST_AUTH_TOKEN_MODEL = 'account.models.Token'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'edem.authentification.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30,
    'DATE_FORMAT': '%d.%m.%Y',
    #    'DEFAULT_RENDERER_CLASSES': (
    #        'rest_framework.renderers.JSONRenderer',
    #    )
}
SHORT_PAGINATION = 10
DEFAULT_PAGINATION = 20

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'testzormail@gmail.com'
EMAIL_HOST_PASSWORD = 'testzorpassword'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'testzormail@gmail.com'

import djcelery

djcelery.setup_loader()

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Kiev'
CELERY_ENABLE_UTC = True
CELERY_TASK_RESULT_EXPIRES = 7 * 86400  # 7 days
CELERY_SEND_EVENTS = True

CELERYBEAT_SCHEDULE = {
    'create_deals': {
        'task': 'create_new_deals',
        'schedule': 3600
    },
    'update_deals': {
        'task': 'deals_to_expired',
        'schedule': 3600
    },
}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'account.serializers.UserSerializer',
}
OLD_PASSWORD_FIELD_ENABLED = True

# SESSION_COOKIE_AGE = 1
SITE_DOMAIN_URL = 'http://vocrm.org/'

# ADMINS = (('Iskander', 'zumichke@gmail.com'), )
ARCHONS = [1, ]
AXES_COOLOFF_TIME = 1
