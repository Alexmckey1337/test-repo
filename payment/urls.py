# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from payment import views

payment_urlpatterns = [
    url(r'^payments/(?P<pk>\d+)/$', views.PaymentUpdateDestroyView.as_view(), name='payment-delete'),
    url(r'^payments/(?P<pk>\d+)/$', views.PaymentUpdateDestroyView.as_view(), name='payment-update'),
    url(r'^payments/(?P<pk>\d+)/detail/$', views.PaymentDetailView.as_view(), name='payment-detail'),
    url(r'^payments/$', views.PaymentListView.as_view(), name='payment-list'),
    url(r'^payments/deal/$', views.PaymentDealListView.as_view(), name='payment-deal-list'),
    url(r'^payments/church_report/$', views.PaymentChurchReportListView.as_view(), name='payment-church_report-list'),
    url(r'^payments/(?P<pk>\d+)/detail/$', views.PaymentDetailView.as_view(), name='payment-detail'),
    url(r'^payments/export/$', views.PaymentExportView.as_view(), name='payment-export'),
]

urlpatterns = [
    url(r'^v1.0/', include(payment_urlpatterns)),
]
