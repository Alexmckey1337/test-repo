from .local_settings import *

DATABASES['default']['TEST'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'test_crm',
    'OPTIONS': {
        "init_command": "SET default_storage_engine=MYISAM",
    }
}
