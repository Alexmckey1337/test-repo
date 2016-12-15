# -*- coding: utf-8
from __future__ import unicode_literals

from .settings import *  # noqa

DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crm_db',
        'USER': 'crm_user',
        'PASSWORD': 'crm_pass',
        'HOST': 'localhost',
        'TEST': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'test_crm',
            'USER': 'crm_user',
            'PASSWORD': '123456',
        }
    }
}
