# -*- coding: utf-8
from __future__ import unicode_literals

from django.urls import include, path
from rest_framework import routers

from apps.event.api import views

router_v1_0 = routers.DefaultRouter()

router_v1_0.register('home_meetings', views.MeetingViewSet)
router_v1_0.register('church_reports', views.ChurchReportViewSet)

urlpatterns = [
    path('v1.0/events/', include(router_v1_0.urls)),
]
