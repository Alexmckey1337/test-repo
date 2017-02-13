# -*- coding: utf-8
from __future__ import unicode_literals

from django.apps import AppConfig


class NavigationConfig(AppConfig):
    name = 'navigation'
    label = 'navigation'

    def ready(self):
        from . import receivers  # noqa
