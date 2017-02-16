# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser
from payment.models import Payment, Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'name', 'code', 'short_name', 'symbol')


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'middle_name')


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('sum', 'currency_sum', 'sent_date', 'rate', 'description', 'manager', 'content_type', 'object_id')


class PaymentShowSerializer(serializers.ModelSerializer):
    currency_sum = CurrencySerializer()
    currency_rate = CurrencySerializer()
    manager = ManagerSerializer()
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')

    class Meta:
        model = Payment
        fields = ('sum', 'effective_sum',
                  'sum_str', 'effective_sum_str',
                  'currency_sum', 'currency_rate', 'rate', 'description',
                  'created_at', 'sent_date',
                  'manager')
