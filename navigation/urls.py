# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import update_columns

urlpatterns = [
    url(r'^update_columns', update_columns),
]
