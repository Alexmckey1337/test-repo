# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from tv_crm import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'tv_call', views.LastCallViewSet)
router_v1_0.register(r'tv_call_stat', views.CallStatViewSet, base_name='tv_call_stat')
router_v1_0.register(r'synopsis', views.SynopsisViewSet)

custom_urls = [
    url(r'^update_last_call/$', views.update_last_call),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
