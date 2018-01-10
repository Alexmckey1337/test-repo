# -*- coding: utf-8
from __future__ import unicode_literals

from django.urls import path

from apps.payment import views

urlpatterns = [
    path('payment/deal/<int:pk>/', views.DealPaymentView.as_view(), name='payment-deal'),
]
