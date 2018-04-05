from django.apps import AppConfig


class PartnershipConfig(AppConfig):
    name = 'apps.partnership'

    def ready(self):
        from . import receivers  # noqa
