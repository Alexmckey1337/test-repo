# -*- coding: utf-8
from __future__ import unicode_literals

from .base import *

BASE_DIR = environ.Path(__file__) - 3

DEBUG = True
ALLOWED_HOSTS = ['crm.local', '127.0.0.1']

INSTALLED_APPS += (
    'django_extensions',
    'rest_framework_swagger',
    # 'debug_toolbar',
)
# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
#
# DEBUG_TOOLBAR_CONFIG = {
#     'DISABLE_PANELS': [
#         'debug_toolbar.panels.redirects.RedirectsPanel',
#     ],
#     'SHOW_TEMPLATE_CONTEXT': True,
# }
# INTERNAL_IPS = ['127.0.0.1', '127.0.1.1', '127.0.2.1', '10.0.2.2', ]

SITE_DOMAIN_URL = 'crm.local:8000'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATIC_ROOT = None
STATICFILES_DIRS = (str(BASE_DIR.path('public/static')),)
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'crm2',
        'USER': 'crmuse',
        'PASSWORD': '123456',
        'OPTIONS': {
            "init_command": "SET default_storage_engine=MYISAM",
        }
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crm_db',
        'USER': 'crm_user',
        'PASSWORD': 'crm_pass',
        'HOST': 'localhost',
    }
}
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}
PAGE_SIZE = 30
