# -*- coding: utf-8
from __future__ import unicode_literals

from django.apps import AppConfig


class PartnershipConfig(AppConfig):
    name = 'apps.partnership'

    def ready(self):
        from . import receivers  # noqa
