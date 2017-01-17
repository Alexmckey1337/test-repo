# -*- coding: utf-8
from __future__ import unicode_literals
from django.conf.urls import url, include
from rest_framework import routers

from group import views


router_v1_1 = routers.DefaultRouter()
router_v1_1.register(r'churches', views.ChurchViewSet)
router_v1_1.register(r'home_groups', views.HomeGroupViewSet)

urlpatterns = [
    url(r'^v1.1/', include(router_v1_1.urls)),
]
