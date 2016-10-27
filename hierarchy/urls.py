# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from hierarchy import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'hierarchy', views.HierarchyViewSet)
router_v1_0.register(r'departments', views.DepartmentViewSet)

custom_urls = [
    url(r'^create_department/$', views.create_department),
    url(r'^delete_department/$', views.delete_department),
    url(r'^update_department/$', views.update_department),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
