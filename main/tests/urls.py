# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include

from apps.payment import views

urlpatterns = [
    url(r'^payment/deal/(?P<pk>\d+)/$', views.DealPaymentView.as_view(), name='payment-deal'),
    url(r'^', include('edem.urls'))
]
