# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from account import views, old_views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'short_users', views.UserShortViewSet, base_name='short_users')
router_v1_0.register(r'exist_users', views.ExistUserListViewSet, base_name='exist_users')

router_v1_1 = routers.DefaultRouter()
router_v1_1.register(r'users', views.UserViewSet, base_name='users_v1_1')

custom_urls = [
    url(r'^login/$', old_views.login_view),
    url(r'^logout/$', views.LogoutView.as_view(), name="logout"),
    url(r'^password_forgot/$', old_views.password_forgot, ),
    url(r'^password_view/$', old_views.password_view, ),
]

custom_v1_1_urls = [
    url(r'^users/for_select/$', views.UserForSelectView.as_view(), name="users-select"),
]

urlpatterns = [
    url(r'^v1.0/', include(custom_urls)),
    url(r'^v1.0/', include(router_v1_0.urls)),

    url(r'^v1.1/', include(custom_v1_1_urls)),
    url(r'^v1.1/', include(router_v1_1.urls)),
]
