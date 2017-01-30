# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from event import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'event_types', views.EventTypeViewSet)
router_v1_0.register(r'event_ankets', views.EventAnketViewSet)
router_v1_0.register(r'events', views.EventViewSet)
router_v1_0.register(r'participations', views.ParticipationViewSet)

router_v1_0.register(r'meetings', views.MeetingViewSet)

custom_urls = [
    # url(r'^create_event/$', views.create_event),
    # url(r'^delete_event/$', views.delete_event),
    # url(r'^create_participations/$', views.create_participations),
    url(r'^update_participation/$', views.update_participation),
    url(r'^create_meeting/$', views.CreateMeetingView.as_view()),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
