# -*- coding: utf-8
from __future__ import unicode_literals

from django.urls import path

from apps.navigation.api import views

urlpatterns = [
    path('update_columns/', views.redis_update_columns),
]
