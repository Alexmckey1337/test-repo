from django.apps import AppConfig


class PartnershipConfig(AppConfig):
    name = 'partnership'

    def ready(self):
        from . import receivers  # noqa
