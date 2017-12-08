# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.reverse import reverse

from account.models import CustomUser
from partnership.models import Partnership, Deal, ChurchDeal
from payment.models import Payment, Currency
from summit.models import SummitAnket
from event.models import ChurchReport
from decimal import Decimal


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
        fields = ('sum', 'currency_sum', 'sent_date', 'rate', 'operation',
                  'description', 'manager', 'content_type', 'object_id')

    def validate(self, data):
        object_currency = data['content_type'].get_object_for_this_type(id=data['object_id']).currency
        if data['currency_sum'] != object_currency and data['rate'] == Decimal(1):
            raise serializers.ValidationError('Проверьте корректность введенного курса')

        return data


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('sum', 'currency_sum', 'sent_date', 'rate', 'operation', 'description', 'object_id')


class PurposeRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Deal):
            return reverse('deal-detail', kwargs={'pk': value.id})
        elif isinstance(value, ChurchDeal):
            return reverse('churchdeal-detail', kwargs={'pk': value.id})
        elif isinstance(value, Partnership):
            return reverse('partner-detail', kwargs={'pk': value.id})
        elif isinstance(value, SummitAnket):
            return reverse('summit_profiles-detail', kwargs={'pk': value.id})
        elif isinstance(value, ChurchReport):
            return reverse('events:church_report_detail', kwargs={'pk': value.id})
        raise Exception('Unexpected type of tagged object')


class DealRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return reverse('deal-detail', kwargs={'pk': value})


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
                  'sum_str', 'effective_sum_str', 'operation',
                  'currency_sum', 'currency_rate', 'rate', 'description',
                  'created_at', 'sent_date', 'manager', 'purpose')


class PaymentShowWithUrlSerializer(serializers.HyperlinkedModelSerializer):
    currency_sum = CurrencySerializer()
    currency_rate = CurrencySerializer()
    manager = ManagerSerializer()
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    sent_date = serializers.DateTimeField(format='%d.%m.%Y')
    purpose = PurposeRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'url', 'sum', 'effective_sum',
                  'sum_str', 'effective_sum_str', 'operation',
                  'currency_sum', 'currency_rate', 'rate', 'description',
                  'created_at', 'sent_date',
                  'manager', 'purpose')


class PaymentDealShowSerializer(PaymentShowSerializer):
    purpose = DealRelatedField(read_only=True, source='object_id')
    purpose_fio = serializers.CharField()
    purpose_date = serializers.DateField(format="%m.%Y")
    purpose_manager_fio = serializers.CharField()
    purpose_type = serializers.IntegerField(read_only=True)
    purpose_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'sum', 'effective_sum',
                  'sum_str', 'effective_sum_str', 'operation',
                  'currency_sum', 'currency_rate', 'rate', 'description',
                  'created_at', 'sent_date',
                  'manager', 'purpose', 'purpose_fio', 'purpose_date', 'purpose_manager_fio',
                  'purpose_type', 'purpose_id')


class PaymentChurchReportShowSerializer(PaymentShowSerializer):
    church_title = serializers.CharField()
    church_id = serializers.IntegerField()
    pastor_fio = serializers.CharField()
    pastor_id = serializers.IntegerField()
    report_date = serializers.DateField(format="%d.%m.%Y")

    class Meta:
        model = Payment
        fields = ('id', 'sum', 'effective_sum',
                  'sum_str', 'effective_sum_str', 'operation',
                  'currency_sum', 'currency_rate', 'rate', 'description',
                  'created_at', 'sent_date', 'manager',
                  'church_title', 'church_id', 'pastor_fio', 'pastor_id', 'report_date')

        read_only_fields = ['__all__']
