# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from apps.navigation.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'tables', views.TableViewSet)
router_v1_0.register(r'columnTypes', views.ColumnTypeViewSet)
router_v1_0.register(r'columns', views.ColumnViewSet)

custom_urls = [
    url(r'^update_columns/$', views.redis_update_columns),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
