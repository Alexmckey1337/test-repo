# -*- coding: utf-8
from __future__ import unicode_literals

from .base import *  # noqa

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False

SECRET_KEY = env('DJANGO_SECRET_KEY', default='CHANGEME!!!')

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

# In-memory email backend stores messages in django.core.mail.outbox
# for unit testing purposes
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

TEST_RUNNER = 'edem.runner.PytestTestRunner'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'crm_db',
#         'USER': 'crm_user',
#         'PASSWORD': 'crm_pass',
#         'HOST': 'localhost',
#         'TEST': {
#             'ENGINE': 'django.db.backends.postgresql_psycopg2',
#             'NAME': 'test_crm',
#             'USER': 'crm_user',
#             'PASSWORD': '123456',
#         }
#     }
# }
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# TEMPLATE LOADERS
# ------------------------------------------------------------------------------
# Keep templates in memory so tests run faster
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
