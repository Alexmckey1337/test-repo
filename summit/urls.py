# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from summit import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'summit', views.SummitViewSet)
router_v1_0.register(r'summit_ankets', views.SummitAnketTableViewSet)
router_v1_0.register(r'summit_types', views.SummitTypeViewSet)
router_v1_0.register(r'summit_search', views.SummitUnregisterUserViewSet, base_name='summit_search')
router_v1_0.register(r'summit_lessons', views.SummitLessonViewSet)
router_v1_0.register(r'summit_ankets_with_notes', views.SummitAnketWithNotesViewSet,
                     base_name='ankets_with_notes')

custom_urls = [
    url(r'^generate_code/.+\.pdf', views.generate_code, name='generate_code'),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
