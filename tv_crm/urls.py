# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from views import update_last_call

urlpatterns = [
    url(r'^update_last_call', update_last_call),
    # url(r'^login', login_view),
    # url(r'^create_user', create_user),
    # url(r'^change_password', change_password),
]
