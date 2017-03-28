# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url
from payment import views

urlpatterns = [
    url(r'^payment/(?P<pk>\d+)/$', views.PaymentUpdateDestroyView.as_view()),
    url(r'^payments/$', views.PaymentListView.as_view()),
]
