# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.serializers import UserTableSerializer
from common.fields import DecimalWithCurrencyField
from payment.serializers import CurrencySerializer
from .models import Partnership, Deal


class PartnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = ('responsible', 'value', 'date', 'need_text', 'currency', 'is_active')


class PartnershipTableSerializer(serializers.ModelSerializer):
    user = UserTableSerializer()
    date = serializers.DateField(format=None, input_formats=None)
    responsible = serializers.StringRelatedField()
    value = DecimalWithCurrencyField(max_digits=12, decimal_places=0, read_only=True, currency_field='currency')

    class Meta:
        model = Partnership
        fields = (
            'id', 'user', 'responsible', 'value', 'is_responsible', 'date',
            'fullname', 'need_text', 'level', 'currency', 'is_active',
        )


class DealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('partnership', 'date', 'date_created',
                  'value', 'description',
                  )


class DealUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('done', 'description')


class DealSerializer(DealCreateSerializer):
    date = serializers.DateField(format=None, input_formats=None, read_only=True)
    date_created = serializers.DateField(input_formats=None)
    partnership = serializers.PrimaryKeyRelatedField(queryset=Partnership.objects.all())
    full_name = serializers.CharField(read_only=True)
    value = serializers.CharField(read_only=True, source='value_str')
    responsible_name = serializers.CharField(read_only=True)
    total_sum = DecimalWithCurrencyField(max_digits=12, decimal_places=0, read_only=True, currency_field='currency')
    currency = CurrencySerializer()
    payment_status = serializers.IntegerField()

    class Meta(DealCreateSerializer.Meta):
        fields = ('id', 'partnership', 'date', 'date_created',
                  'value', 'done', 'expired', 'description',
                  'full_name', 'responsible_name', 'partner_link',
                  'total_sum', 'currency', 'payment_status',
                  )


class PartnershipManagerSummarySerializers(serializers.ModelSerializer):
    manager = serializers.CharField()
    sum_deals = serializers.DecimalField(max_digits=12, decimal_places=0)
    sum_pay = serializers.DecimalField(max_digits=12, decimal_places=0)
    plan = serializers.DecimalField(max_digits=12, decimal_places=0)
    percent_of_plan = serializers.DecimalField(max_digits=12, decimal_places=1)
    potential_sum = serializers.DecimalField(max_digits=12, decimal_places=0)
    total_partners = serializers.IntegerField(read_only=True)
    active_partners = serializers.IntegerField(read_only=True)

    class Meta:
        model = Partnership
        fields = ('manager', 'sum_deals', 'sum_pay', 'plan', 'percent_of_plan', 'potential_sum',
                  'total_partners', 'active_partners')
