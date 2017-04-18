# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from partnership import views

router_v1_1 = routers.DefaultRouter()
router_v1_1.register(r'partnerships', views.PartnershipViewSet, base_name='partner')

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'deals', views.DealViewSet)

custom_urls = [
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),
    url(r'^v1.1/', include(router_v1_1.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
