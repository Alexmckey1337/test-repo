# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.reverse import reverse

from account.models import CustomUser
from partnership.models import Partnership, Deal
from payment.models import Payment, Currency
from summit.models import SummitAnket


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


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('sum', 'currency_sum', 'sent_date', 'rate', 'description', 'object_id')


class PurposeRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Deal):
            return reverse('deal-detail', kwargs={'pk': value.id})
        elif isinstance(value, Partnership):
            return reverse('partnerships_v1_1-detail', kwargs={'pk': value.id})
        elif isinstance(value, SummitAnket):
            return reverse('summit_ankets-detail', kwargs={'pk': value.id})
        raise Exception('Unexpected type of tagged object')


class PaymentShowSerializer(serializers.ModelSerializer):
    currency_sum = CurrencySerializer()
    currency_rate = CurrencySerializer()
    manager = ManagerSerializer()
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    sent_date = serializers.DateTimeField(format='%d.%m.%Y')
    purpose = PurposeRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'sum', 'effective_sum',
                  'sum_str', 'effective_sum_str',
                  'currency_sum', 'currency_rate', 'rate', 'description',
                  'created_at', 'sent_date',
                  'manager', 'purpose')
