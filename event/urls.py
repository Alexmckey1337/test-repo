# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from event import views

router_v1_0 = routers.DefaultRouter()

router_v1_0.register(r'home_meetings', views.MeetingViewSet)
router_v1_0.register(r'church_reports', views.ChurchReportViewSet)

urlpatterns = [
    url(r'^v1.0/events/', include(router_v1_0.urls)),
]
