# -*- coding: utf-8
from __future__ import unicode_literals

from django.urls import path, include
from rest_framework import routers

from apps.hierarchy.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('hierarchy', views.HierarchyViewSet)
router_v1_0.register('departments', views.DepartmentViewSet)

custom_urls = [
]

urlpatterns = [
    path('v1.0/', include(router_v1_0.urls)),

    path('v1.0/', include(custom_urls)),
]
