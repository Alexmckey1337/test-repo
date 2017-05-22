import os

import logging
import raven
# from django.utils import six

from .base import *  # noqa

# from boto.s3.connection import OrdinaryCallingFormat

SECRET_KEY = env('DJANGO_SECRET_KEY')

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_MIDDLEWARE = (
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
)
MIDDLEWARE = RAVEN_MIDDLEWARE + MIDDLEWARE

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


if os.environ.get('USE_DOCKER') == 'yes':
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "asgi_redis.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("redis", 6379)],
            },
            "ROUTING": "edem.routing.channel_routing",
        },
    }
    CACHES = {
        "default": {
            'BACKEND': 'redis_cache.cache.RedisCache',
            'LOCATION': 'redis:6379',
        },
    }

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/1.9/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/ja/1.9/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
#     'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
# SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
#     'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
# SECURE_BROWSER_XSS_FILTER = True
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
# # SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
# SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=False)
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
# X_FRAME_OPTIONS = 'DENY'

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['vocrm.org', '127.0.2.1', 'crm.local'])

INSTALLED_APPS += ('gunicorn', )

# # STORAGE CONFIGURATION
# # ------------------------------------------------------------------------------
# # Uploaded Media Files
# # ------------------------
# # See: http://django-storages.readthedocs.io/en/latest/index.html
# INSTALLED_APPS += (
#     'storages',
# )
#
# AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
# AWS_AUTO_CREATE_BUCKET = True
# AWS_QUERYSTRING_AUTH = False
# AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()
#
# # AWS cache settings, don't change unless you know what you're doing:
# AWS_EXPIRY = 60 * 60 * 24 * 7
#
# # TODO See: https://github.com/jschneier/django-storages/issues/47
# # Revert the following and use str after the above-mentioned bug is fixed in
# # either django-storage-redux or boto
# AWS_HEADERS = {
#     'Cache-Control': six.b('max-age=%d, s-maxage=%d, must-revalidate' % (
#         AWS_EXPIRY, AWS_EXPIRY))
# }
#
# # URL that handles the media served from MEDIA_ROOT, used for managing
# # stored files.
#
# #  See:http://stackoverflow.com/questions/10390244/
# from storages.backends.s3boto import S3BotoStorage
# StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
# MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')
# DEFAULT_FILE_STORAGE = 'config.settings.production.MediaRootS3BotoStorage'
#
# MEDIA_URL = 'https://s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME
#
# # Static Assets
# # ------------------------
#
# STATIC_URL = 'https://s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME
# STATICFILES_STORAGE = 'config.settings.production.StaticRootS3BotoStorage'
# # See: https://github.com/antonagestam/collectfast
# # For Django 1.7+, 'collectfast' should come before
# # 'django.contrib.staticfiles'
# AWS_PRELOAD_METADATA = True
# INSTALLED_APPS = ('collectfast', ) + INSTALLED_APPS

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------

# Use the Heroku-style specification
# Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES['default'] = env.db('DATABASE_URL')

REDIS_LOCATION = '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0)
# Heroku URL does not pass the DB number, so we parse it in
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
            # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        }
    }
}

SENTRY_DSN = env('DJANGO_SENTRY_DSN', default='')
SENTRY_CLIENT = env('DJANGO_SENTRY_CLIENT', default='raven.contrib.django.raven_compat.DjangoClient')

LOGGING['root'] = {
    'level': 'WARNING',
    'handlers': ['sentry', 'console'],
    'filters': ['require_debug_false'],
}
LOGGING['handlers']['sentry'] = {
    'level': 'WARNING',  # To capture more than ERROR, change to WARNING, INFO, etc.
    'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    'tags': {'custom-tag': 'x'},
    'filters': ['require_debug_false'],
}
LOGGING['loggers']['account.views'] = {
    'level': 'INFO',
    'handlers': ['console', 'sentry'],
    'propagate': False,
}
LOGGING['loggers']['event.views'] = {
    'level': 'INFO',
    'handlers': ['console', 'sentry'],
    'propagate': False,
}
LOGGING['loggers']['summit.views'] = {
    'level': 'INFO',
    'handlers': ['console', 'sentry'],
    'propagate': False,
}
SENTRY_CELERY_LOGLEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)
RAVEN_CONFIG = {
    'CELERY_LOGLEVEL': env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO),
    'DSN': SENTRY_DSN,
}
if not os.environ.get('USE_DOCKER') == 'yes':
    RAVEN_CONFIG['RELEASE'] = raven.fetch_git_sha(os.path.dirname(os.pardir))
