# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from account import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'users', views.UserViewSet, base_name='customuser')
router_v1_0.register(r'short_users', views.UserShortViewSet, base_name='short_users')

router_v1_1 = routers.DefaultRouter()
router_v1_1.register(r'users', views.NewUserViewSet, base_name='users_v1_1')

custom_urls = [
    url(r'^ping_user_key/$', views.ping_user_key),
    url(r'^delete_user/$', views.delete_user),
    url(r'^login/$', views.login_view),
    url(r'^create_user/$', views.create_user),
    url(r'^send_password/$', views.send_password),
    url(r'^change_password/$', views.change_password),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^download_image/$', views.download_image),
    url(r'^password_forgot/$', views.password_forgot, ),
    url(r'^password_view/$', views.password_view, ),
    url(r'^password_view/(?P<activation_key>\w+)/$', views.password_view),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),
    url(r'^v1.1/', include(router_v1_1.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
