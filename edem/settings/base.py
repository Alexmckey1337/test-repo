import environ
from django.utils.translation import ugettext_lazy as _

from apps.account.utils import create_token

BASE_DIR = environ.Path(__file__) - 3

env = environ.Env()
env.read_env(env_file=str(BASE_DIR.path('.env')))

FILEBROWSER_DIRECTORY = 'uploads'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4y6l3@a0%vq394z6+w)k3-wl459r++v=z!jv1gw4+nt0sd5z+s'

ASTERISK_SERVICE_ADDRESS = 'http://asterisk:8080'
VISITORS_LOCATION_TOKEN = '4ewfeciss6qdbmgfj9eg6jb3fdcxefrs4dxtcdrt10rduds2sn'

APP_DEVICE_ID_FIELD = 'HTTP_DEVICE_ID'
APP_DEVICE_ID_EXPIRE = 30 * 24 * 60 * 60  # 30 days

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = env.bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = ['vocrm.net']

# Application definition
DJANGO_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.postgres',
)
THIRD_PARTY_APPS = (
    'import_export',
    'rest_framework',
    # 'rest_framework.authtoken',
    'django_filters',

    'rest_auth',
    'corsheaders',
    'tinymce',
    # 'rest_auth.registration',
    'django_extensions',
    'channels',
    'drf_yasg',
)
LOCAL_APPS = (
    'main',
    'apps.account.apps.AccountConfig',
    'apps.analytics.apps.AnalyticsConfig',
    'apps.event.apps.EventsConfig',
    'apps.group.apps.GroupConfig',
    'apps.hierarchy.apps.HierarchyConfig',
    'apps.location.apps.LocationConfig',
    'apps.navigation.apps.NavigationConfig',
    'apps.notification.apps.NotificationConfig',
    'apps.partnership.apps.PartnershipConfig',
    'apps.payment.apps.PaymentConfig',
    'apps.report.apps.ReportConfig',
    'apps.status.apps.StatusConfig',
    'apps.summit.apps.SummitConfig',
    'apps.task.apps.TaskConfig',
    'apps.zmail.apps.ZMailConfig',
    'apps.controls.apps.ControlsConfig',
    'apps.help.apps.HelpConfig',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = (
    'common.middleware.AnalyticsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'common.middleware.HardAuthenticationMiddleware',
    'common.middleware.ManagerAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
CORS_ORIGIN_ALLOW_ALL = True

CACHES = {
    "default": {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace,fullpage",
    'theme': "advanced",
    'relative_urls': False,
    'convert_urls': False,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'width': '100%',
    'height': '1000',
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
                'apps.notification.context_processor.notifications',
                'common.context_processor.true_false_options',
                'apps.account.context_processor.spiritual_levels',
                'apps.partnership.context_processor.partner_levels'
            ],
        },
    },
]
TEMPLATE_DEBUG = DEBUG

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
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGES = (
    ('ru', _('Russian')),
    # ('uk', _('Ukrainian')),
    # ('en', _('English')),
)

LANGUAGE_CODE = 'ru-RU'
DEFAULT_LANGUAGE = 'ru-RU'
USE_I18N = True
SITE_ID = 1
TIME_ZONE = 'UTC'
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = (str(BASE_DIR.path('locale')),)

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
    'apps.account.auth_backends.CustomUserModelBackend',
    'apps.account.auth_backends.LoginByIdBackend',
)

CUSTOM_USER_MODEL = 'apps.account.CustomUser'
DATE_FORMAT = 'd.m.Y'
DATETIME_FORMAT = 'd.m.Y H:i:s'
TIME_FORMAT = 'H:i:s'
SHORT_DATE_FORMAT = 'd.m.Y'

REST_AUTH_TOKEN_CREATOR = create_token
REST_AUTH_TOKEN_MODEL = 'apps.account.models.Token'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'edem.authentification.CsrfExemptSessionAuthentication',
        'apps.account.auth_backends.CustomUserTokenAuthentication',
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

SEND_PULSE_GRANT_TYPE = 'client_credentials'
SEND_PULSE_CLIENT_ID = '2d90c1e2ae67901897d7536b2670bb8f'
SEND_PULSE_CLIENT_SECRET = '47e1fc014543cde0c1fcb931f9148cc8'

EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'testzormail@gmail.com'
EMAIL_HOST_PASSWORD = 'testzorpassword'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'testzormail@gmail.com'

#  CELERY
INSTALLED_APPS += ('edem.settings.celery.CeleryConfig',)
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

from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'create_deals': {
        'task': 'create_new_deals',
        'schedule': 3600
    },
    'update_deals': {
        'task': 'deals_to_expired',
        'schedule': 3600
    },
    # Executes every monday evening at 00:00 A.M
    'processing_home_meetings': {
        'task': 'processing_home_meetings',
        'schedule': crontab(hour=5, minute=0, day_of_week='mon')
    },
    # Executes every monday evening at 20:00 A.M
    'processing_church_reports': {
        'task': 'processing_church_reports',
        'schedule': crontab(hour=8, minute=0, day_of_week=2)
    },
    'delete_expired_export': {
        'task': 'delete_expired_export',
        'schedule': crontab(hour=5, minute=0)
    },
    # 'telegram_users_to_kick': {
    #     'task': 'telegram_users_to_kick',
    #     'schedule': crontab(minute=0, hour=0)
    # },
    'trainee_group_members_deactivate': {
        'task': 'trainee_group_members_deactivate',
        'schedule': crontab(minute=0, hour=3)
    },
    'kick_from_telegram_groups': {
        'task': 'kick_from_telegram_groups',
        'schedule': crontab(minute=0, hour=3)
    },
    'improve_convert_to_congregation': {
        'task': 'improve_convert_to_congregation',
        'schedule': 3600
    },
    'users_is_stable_review': {
        'task': 'users_is_stable_review',
        'schedule': crontab(hour=6, minute=0, day_of_week='mon')
    }
}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.account.api.serializers.UserSerializer',
    'LOGIN_SERIALIZER': 'apps.account.api.serializers.RestAuthLoginSerializer'
}
OLD_PASSWORD_FIELD_ENABLED = True

# SESSION_COOKIE_AGE = 1
SITE_DOMAIN_URL = 'https://vocrm.net/'

# ADMINS = (('Iskander', 'zumichke@gmail.com'), )
ARCHONS = [1, ]
AXES_COOLOFF_TIME = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s || %(asctime)s || '
                      '%(module)s || %(name)s || %(lineno)d || '
                      '%(message)s'
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
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'middleware': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'apps.account.api.views': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'apps.event.api.views': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'apps.group.api.views': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'apps.summit.api.views': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'apps.partnership.api.tasks': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'partner.sql': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'performance': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
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

# Partnership

# levels

PARTNER_LEVELS = {
    'director': 0,
    'supervisor': 1,
    'manager': 2,
}

SUMMIT_ANKET_ROLES = {
    'visitor': 10,
    'consultant': 20,
    'supervisor': 30
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
        "ROUTING": "edem.routing.channel_routing",
    },
}

HIERARCHIES = (
    dict(title='Гость', level=0),
    dict(title='Прихожанин', level=0),
    dict(title='Лидер', level=1),
    dict(title='Пастор', level=2),
    dict(title='Сотник (Отв-й за 5 ячеек)', level=2),
    dict(title='Ответственный Киев', level=4),
    dict(title='Епископ', level=4),
    dict(title='Главный епископ', level=50),
    dict(title='Старший епископ', level=60),
    dict(title='Апостол', level=70),
    dict(title='Архонт', level=80),
)

CHANGE_HIERARCHY_LEVELS = {
    -10: set(),
    0: set(),
    1: {0},
    2: {0, 1, 2},
    4: {0, 1, 2, 4},
    50: {0, 1, 2, 4},
    60: {0, 1, 2, 4, 50},
    70: {0, 1, 2, 4, 60},
    80: {0, 1, 2, 4, 60, 70, 80},
}

NEW_TICKET_STATUS = {
    'none': 'download',
    'download': 'print',
    'print': 'given',
    'given': 'print',
}

DEFAULT_SITE_SETTINGS = {
    "partners": {
        # Минимальная сумма партнерских пожертвований для получения VIP статуса
        "vip_status": {"uah": 12500, "usd": 500, "rur": 30000, "eur": 400},
        "ruby_status": {"uah": 6000, "usd": 250, "rur": 15000, "eur": 200},
    },
    # Срок после покаяния чтобы Новообращенный автоматически был повышен до Прихожанина
    "convert_experience": {"value": 6, "unit": "month"},
}

# Notifications

NOTIFICATION_REDIS_HOST = 'redis'
