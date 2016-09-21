# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import create_department, update_department, delete_department

urlpatterns = [
    url(r'^create_department', create_department),
    url(r'^delete_department', delete_department),
    url(r'^update_department', update_department),
]
