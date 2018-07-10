from django.conf import settings

USER_MODEL = getattr(settings, 'LIGHT_AUTH_USER_MODEL', 'account.CustomUser')
EMAIL_CONFIRMATION_EXPIRE_DAYS = getattr(settings, 'LIGHT_AUTH_EMAIL_CONFIRMATION_EXPIRE_DAYS', 3)
