import os

import raven

from .base import *

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': 'http://0f03c3eb3b8648809252995dfa6b94ba:efb79021d0874228b30115facae051f1@146.185.159.174:9000/2',
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

MIDDLEWARE_CLASSES = ('raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',) + MIDDLEWARE_CLASSES

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
