from django.apps import AppConfig


class SummitConfig(AppConfig):
    name = 'apps.summit'

    def ready(self):
        from . import receivers  # noqa
