from django.conf import settings

CELERY_QUEUE = getattr(settings, 'ZMAIL_CELERY_QUEUE', 'default')
ENABLE_CELERY = getattr(settings, 'ZMAIL_ENABLE_CELERY', True)
SEND_MAX_TIME = getattr(settings, 'ZMAIL_SEND_MAX_TIME', 60)
SEND_RETRY_DELAY = getattr(settings, 'ZMAIL_SEND_RETRY_DELAY', 10 * 60)
SEND_RETRY = getattr(settings, 'ZMAIL_SEND_RETRY', 0)
