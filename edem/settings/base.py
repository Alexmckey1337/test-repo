from __future__ import unicode_literals

"""
Django settings for edem project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import environ

from account.utils import create_token

BASE_DIR = environ.Path(__file__) - 3
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env.read_env(env_file=str(BASE_DIR.path('.env')))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4y6l3@a0%vq394z6+w)k3-wl459r++v=z!jv1gw4+nt0sd5z+s'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = env.bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = ['vocrm.org']

# Application definition
DJANGO_APPS = (
    'django.contrib.contenttypes',
    'grappelli.dashboard',
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites'
)
THIRD_PARTY_APPS = (
    'import_export',
    'rest_framework',
    # 'rest_framework.authtoken',
    'djcelery',

    'rest_auth',
    'corsheaders',
    'dbmail',
    'tinymce',
    # 'rest_auth.registration',
    'mptt',
)
LOCAL_APPS = (
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
    'payment',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CACHES = {
    "default": {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
    },
}

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace,fullpage",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}

ROOT_URLCONF = 'edem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.path('templates')), ],
        # 'DIRS': [BASE_DIR + '/templates', ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'notification.context_processor.notifications'
            ],
        },
    },
]

WSGI_APPLICATION = 'edem.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///crm_db'),
}

DATABASES['default']['ATOMIC_REQUESTS'] = True
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

GRAPPELLI_SWITCH_USER = True
GRAPPELLI_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
MEDIA_ROOT = str(BASE_DIR.path('public/media'))
# MEDIA_ROOT = os.path.join(BASE_DIR, 'public/media')
MEDIA_URL = '/media/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'public/static')
STATIC_ROOT = str(BASE_DIR.path('public/static'))
STATICFILES_DIRS = []
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

EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'testzormail@gmail.com'
EMAIL_HOST_PASSWORD = 'testzorpassword'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'testzormail@gmail.com'

########## CELERY
INSTALLED_APPS += ('edem.settings.celery.CeleryConfig',)
# if you are not using the django database broker (e.g. rabbitmq, redis, memcached), you can remove the next line.
INSTALLED_APPS += ('kombu.transport.django',)
BROKER_URL = env('CELERY_BROKER_URL', default='django://')
if BROKER_URL == 'django://':
    CELERY_RESULT_BACKEND = 'redis://'
else:
    CELERY_RESULT_BACKEND = BROKER_URL
# BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TIMEZONE = 'Europe/Kiev'
CELERY_ENABLE_UTC = True
CELERY_TASK_RESULT_EXPIRES = 7 * 86400  # 7 days
CELERY_SEND_EVENTS = True
CELERY_DEFAULT_QUEUE = 'default'
CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1

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

import djcelery

djcelery.setup_loader()

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'account.serializers.UserSerializer',
}
OLD_PASSWORD_FIELD_ENABLED = True

# SESSION_COOKIE_AGE = 1
SITE_DOMAIN_URL = 'http://vocrm.org/'

# ADMINS = (('Iskander', 'zumichke@gmail.com'), )
ARCHONS = [1, ]
AXES_COOLOFF_TIME = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        # 'account.views': {
        #     'level': 'DEBUG',
        #     'handlers': ['console', 'sentry'],
        #     'propagate': False,
        # },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
