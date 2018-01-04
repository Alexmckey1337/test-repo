# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from apps.partnership.api import views

router_v1_1 = routers.DefaultRouter()
router_v1_1.register(r'partnerships', views.PartnershipViewSet, base_name='partner')

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'deals', views.DealViewSet)
router_v1_0.register(r'partner_groups', views.PartnerGroupViewSet)

router_v1_0.register(r'church_partners', views.ChurchPartnerViewSet, base_name='church_partner')
router_v1_0.register(r'church_deals', views.ChurchDealViewSet)

custom_urls = [
    url(r'^users/(?P<user_id>\d+)/set_partner_role/$', views.SetPartnerRoleView.as_view(), name="set_partner_role"),
    url(r'^users/(?P<user_id>\d+)/delete_partner_role/$',
        views.DeletePartnerRoleView.as_view(), name="delete_partner_role"),
    url(r'^users/(?P<user_id>\d+)/update_partner_role/$',
        views.UpdatePartnerRoleView.as_view(), name="update_partner_role"),
    url(r'^partners/(?P<partner_id>\d+)/last_deals/$', views.LastPartnerDealsView.as_view(), name="partner-last_deals"),
    url(r'^partners/(?P<partner_id>\d+)/last_payments/$',
        views.LastPartnerPaymentsView.as_view(), name="church_partner-last_payments"),
    url(r'^church_partners/(?P<partner_id>\d+)/last_deals/$', views.LastChurchPartnerDealsView.as_view(), name="partner-last_deals"),
    url(r'^church_partners/(?P<partner_id>\d+)/last_payments/$',
        views.LastChurchPartnerPaymentsView.as_view(), name="church_partner-last_payments"),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),
    url(r'^v1.1/', include(router_v1_1.urls)),

    url(r'^v1.0/', include(custom_urls)),
]
