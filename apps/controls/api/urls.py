# -*- coding: utf-8
from __future__ import unicode_literals

from django.urls import path, include
from rest_framework import routers

from apps.controls.api import views

router_v1_0 = routers.DefaultRouter()


router_v1_0.register('db_access', views.DatabaseAccessViewSet)

urlpatterns = [
    path('', include(router_v1_0.urls))
]
