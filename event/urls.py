# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from event import views

router_v1_0 = routers.DefaultRouter()

router_v1_0.register(r'home_meetings', views.MeetingViewSet, base_name='home_meetings')
router_v1_0.register(r'church_reports', views.ChurchReportViewSet, base_name='church_reports')
router_v1_0.register(r'meeting_attends', views.MeetingAttendViewSet, base_name='meeting_attends')

urlpatterns = [
    url(r'^v1.0/events/', include(router_v1_0.urls)),
]
