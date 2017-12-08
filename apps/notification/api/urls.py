# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from apps.notification.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'notifications', views.NotificationViewSet)

custom_urls = [
    # url(r'^entry/$', views.entry, name='entry'),
    # url(r'^events/$', views.events, name='events'),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
