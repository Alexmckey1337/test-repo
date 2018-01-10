# -*- coding: utf-8
from __future__ import unicode_literals

from django.urls import path, include
from rest_framework import routers

from apps.navigation.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('tables', views.TableViewSet)
router_v1_0.register('columnTypes', views.ColumnTypeViewSet)
router_v1_0.register('columns', views.ColumnViewSet)

custom_urls = [
    path('update_columns/', views.redis_update_columns),
]

urlpatterns = [
    path('', include(router_v1_0.urls)),
    path('', include(custom_urls)),
]
