# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from apps.hierarchy.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'hierarchy', views.HierarchyViewSet)
router_v1_0.register(r'departments', views.DepartmentViewSet)

custom_urls = [
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
