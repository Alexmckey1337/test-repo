# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.serializers import UserTableSerializer
from common.fields import DecimalWithCurrencyField
from payment.serializers import CurrencySerializer
from .models import Partnership, Deal
from common.fields import ReadOnlyChoiceField

BASE_PARTNER_FIELDS = ('id', 'responsible', 'value', 'date', 'need_text', 'currency', 'is_active')


class PartnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = BASE_PARTNER_FIELDS


class PartnershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = BASE_PARTNER_FIELDS


class PartnershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = ('user',) + BASE_PARTNER_FIELDS


class PartnershipTableSerializer(serializers.ModelSerializer):
    user = UserTableSerializer()
    date = serializers.DateField(format=None, input_formats=None)
    responsible = serializers.StringRelatedField()
    value = DecimalWithCurrencyField(max_digits=12, decimal_places=0,
                                     read_only=True, currency_field='currency')

    class Meta:
        model = Partnership
        fields = ('id', 'user', 'fullname', 'level', 'is_responsible') + BASE_PARTNER_FIELDS


class DealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('partnership', 'date', 'date_created',
                  'value', 'description', 'type',
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
    total_sum = DecimalWithCurrencyField(max_digits=12, decimal_places=0,
                                         read_only=True, currency_field='currency')
    currency = CurrencySerializer()
    payment_status = serializers.IntegerField()
    type = ReadOnlyChoiceField(choices=Deal.DEAL_TYPE_CHOICES, read_only=True)

    class Meta(DealCreateSerializer.Meta):
        fields = ('id', 'partnership', 'date', 'date_created',
                  'value', 'done', 'expired', 'description',
                  'full_name', 'responsible_name', 'partner_link',
                  'total_sum', 'currency', 'payment_status', 'type',
                  )
