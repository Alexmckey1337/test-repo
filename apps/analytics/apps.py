from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    name = 'apps.analytics'

    def ready(self):
        from . import receivers  # noqa
