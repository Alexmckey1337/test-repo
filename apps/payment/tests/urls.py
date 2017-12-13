# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from apps.payment.api import views

urlpatterns = [
    url(r'^payment/(?P<pk>\d+)/$', views.PaymentUpdateDestroyView.as_view()),
    url(r'^payments/$', views.PaymentListView.as_view()),
    url(r'^payments/deal/$', views.PaymentDealListView.as_view()),
    url(r'^', include('edem.urls'))
]
