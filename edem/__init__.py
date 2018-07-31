from .settings.celery import app as celery_app  # noqa

VERSION = (1, 17, 19)


def get_short_version():
    return f'{VERSION[0]}.{VERSION[1]}'


def get_version():
    return f'{VERSION[0]}.{VERSION[1]}.{VERSION[2]}'


__version__ = get_version()
