# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from payment import views

payment_urlpatterns = [
    url(r'^payments/(?P<pk>\d+)/$', views.PaymentUpdateDestroyView.as_view(), name='payment-delete'),
    url(r'^payments/(?P<pk>\d+)/$', views.PaymentUpdateDestroyView.as_view(), name='payment-update')
]

urlpatterns = [
    url(r'^v1.0/', include(payment_urlpatterns)),
]
