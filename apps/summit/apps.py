# -*- coding: utf-8
from __future__ import unicode_literals

from django.apps import AppConfig


class SummitConfig(AppConfig):
    name = 'apps.summit'

    def ready(self):
        from . import receivers  # noqa
