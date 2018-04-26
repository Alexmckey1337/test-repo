import operator
import re
from functools import reduce

import django_filters
from django.conf import settings
from django.db.models import Q
from rest_framework import filters

from apps.account.models import CustomUser
from apps.hierarchy.models import Hierarchy, Department
from apps.partnership.models import Deal, Partnership, PartnerGroup, ChurchDeal, ChurchPartner
from apps.payment.models import Currency
from common.filters import BaseFilterByBirthday, BaseFilterMasterTree


class DealDateAndValueFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date_created", lookup_expr='gte')
    to_date = django_filters.DateFilter(name="date_created", lookup_expr='lte')
    from_value = django_filters.NumberFilter(name="value", lookup_expr='gte')
    to_value = django_filters.NumberFilter(name="value", lookup_expr='lte')
    group = django_filters.ModelMultipleChoiceFilter(name="partnership__group", queryset=PartnerGroup.objects.all())

    class Meta:
        model = Deal
        fields = ['partnership__responsible', 'currency_id', 'responsible',
                  'value', 'date_created', 'date',
                  'expired', 'done', 'to_date', 'from_date', 'from_value', 'to_value',
                  'group']


class ChurchDateAndValueFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date_created", lookup_expr='gte')
    to_date = django_filters.DateFilter(name="date_created", lookup_expr='lte')
    from_value = django_filters.NumberFilter(name="value", lookup_expr='gte')
    to_value = django_filters.NumberFilter(name="value", lookup_expr='lte')

    class Meta:
        model = ChurchDeal
        fields = ['partnership__responsible', 'currency_id', 'responsible',
                  'value', 'date_created', 'date',
                  'expired', 'done', 'to_date', 'from_date', 'from_value', 'to_value']


class DealFilterByPaymentStatus(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        payment_status = request.query_params.get('payment_status')
        type = request.query_params.get('type')

        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        if type:
            queryset = queryset.filter(type=type)

        return queryset


class PartnerFilterByLevel(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        level = request.query_params.get('level')
        if level:
            queryset = queryset.filter(user__partner_role__level=level)

        return queryset


class PartnerFilterByVIP(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        currencies = Currency.objects.all()
        status = request.query_params.get('vip_status', '')
        vip = settings.DEFAULT_SITE_SETTINGS.get('partners', {}).get('vip_status', {})
        ruby = settings.DEFAULT_SITE_SETTINGS.get('partners', {}).get('ruby_status', {})

        if status == 'vip':
            orm_q = 'value__gte', lambda c: vip[c]
        elif status == 'ruby':
            orm_q = 'value__range', lambda c: (ruby[c], vip[c]-0.001)
        elif status == 'any':
            orm_q = 'value__gte', lambda c: ruby[c]
        elif status == 'empty':
            orm_q = 'value__lt', lambda c: ruby[c]
        else:
            return queryset
        q = list()
        for currency in currencies.filter(code__in=(set(vip.keys()) & set(ruby.keys()))):
            q.append(Q(currency=currency, **{orm_q[0]: orm_q[1](currency.code)}))
        queryset = queryset.filter(reduce(operator.or_, q))

        return queryset


class FilterByPartnerBirthday(BaseFilterByBirthday):
    born_date_field = 'user__born_date'


class FilterPartnerMasterTreeWithSelf(BaseFilterMasterTree):
    include_self_master = True
    user_field_prefix = 'user__'


class PartnerUserFilter(django_filters.FilterSet):
    hierarchy = django_filters.ModelChoiceFilter(name='user__hierarchy', queryset=Hierarchy.objects.all())
    master = django_filters.ModelMultipleChoiceFilter(name="user__master", queryset=CustomUser.objects.all())
    group = django_filters.ModelMultipleChoiceFilter(name="group", queryset=PartnerGroup.objects.all())
    department = django_filters.ModelChoiceFilter(name="user__departments", queryset=Department.objects.all())
    is_active = django_filters.BooleanFilter(name='is_active')
    to_value = django_filters.NumberFilter(name="value", lookup_expr='lte')
    from_value = django_filters.NumberFilter(name="value", lookup_expr='gte')
    from_repentance_date = django_filters.DateFilter(name='user__repentance_date', lookup_expr='gte')
    to_repentance_date = django_filters.DateFilter(name='user__repentance_date', lookup_expr='lte')

    class Meta:
        model = Partnership
        fields = ['master', 'hierarchy', 'department', 'user', 'responsible', 'is_active',
                  'from_repentance_date', 'to_repentance_date', 'group', 'from_value', 'to_value']


class ChurchPartnerFilter(django_filters.FilterSet):
    department = django_filters.ModelMultipleChoiceFilter(name="church__department",
                                                          queryset=Department.objects.all())
    pastor = django_filters.ModelChoiceFilter(name='church__pastor', queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct())
    is_open = django_filters.BooleanFilter(name='church__is_open')
    opening_date = django_filters.DateFilter(name='church__opening_date')

    group = django_filters.ModelMultipleChoiceFilter(name="group", queryset=PartnerGroup.objects.all())
    is_active = django_filters.BooleanFilter(name='is_active')
    to_value = django_filters.NumberFilter(name="value", lookup_expr='lte')
    from_value = django_filters.NumberFilter(name="value", lookup_expr='gte')

    class Meta:
        model = ChurchPartner
        fields = ('department', 'pastor', 'is_open', 'opening_date', 'group', 'is_active', 'from_value', 'to_value')


class PartnerFilterByDateAge(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        age_gt = request.query_params.get('age_gt', '')
        age_lt = request.query_params.get('age_lt', '')

        age_reg = re.compile('(\d+\s*(year|month|day))')
        age_gt = age_reg.search(age_gt)
        age_gt = age_gt.group(0) if age_gt else None
        age_lt = age_reg.search(age_lt)
        age_lt = age_lt.group(0) if age_lt else None

        if age_gt and age_lt:
            return queryset.extra(where=["age(date) BETWEEN INTERVAL %s AND interval %s"], params=[age_gt, age_lt])
        elif age_gt:
            return queryset.extra(where=["age(date) >= INTERVAL %s"], params=[age_gt])
        elif age_lt:
            return queryset.extra(where=["age(date) <= INTERVAL %s"], params=[age_lt])

        return queryset


class LastDealFilter(django_filters.FilterSet):
    class Meta:
        model = Deal
        fields = ('done',)


class LastChurchDealFilter(django_filters.FilterSet):
    class Meta:
        model = ChurchDeal
        fields = ('done',)
