# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from partnership import views

router_v1_1 = routers.DefaultRouter()
router_v1_1.register(r'partnerships', views.NewPartnershipViewSet, base_name='partnerships_v1_1')

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'deals', views.DealViewSet)
router_v1_0.register(r'partnerships', views.PartnershipViewSet)
router_v1_0.register(r'partnerships_unregister_search', views.PartnershipsUnregisterUserViewSet,
                     base_name='partnerships_unregister_search')

custom_urls = [
    url(r'^create_partnership/$', views.create_partnership),
    url(r'^update_partnership/$', views.update_partnership),
    url(r'^delete_partnership/$', views.delete_partnership),
    url(r'^create_deal/$', views.create_deal),
    url(r'^update_deal/$', views.update_deal),
    url(r'^delete_deal/$', views.delete_deal),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),
    url(r'^v1.1/', include(router_v1_1.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
