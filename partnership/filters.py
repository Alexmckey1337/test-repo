import django_filters
import re

from account.models import CustomUser
from common.filters import BaseFilterByBirthday, BaseFilterMasterTree
from hierarchy.models import Hierarchy, Department
from partnership.models import Deal, Partnership, PartnerGroup
from rest_framework import filters
from django.db import connection


class DateAndValueFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date_created", lookup_expr='gte')
    to_date = django_filters.DateFilter(name="date_created", lookup_expr='lte')
    from_value = django_filters.NumberFilter(name="value", lookup_expr='gte')
    to_value = django_filters.NumberFilter(name="value", lookup_expr='lte')

    class Meta:
        model = Deal
        fields = ['partnership__responsible', 'currency_id', 'responsible',
                  'partnership__user', 'value', 'date_created', 'date',
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
    value_to = django_filters.NumberFilter(name="value", lookup_expr='lte')
    value_from = django_filters.NumberFilter(name="value", lookup_expr='gte')
    repentance_date_from = django_filters.DateFilter(name='user__repentance_date', lookup_expr='gte')
    repentance_date_to = django_filters.DateFilter(name='user__repentance_date', lookup_expr='lte')

    class Meta:
        model = Partnership
        fields = ['master', 'hierarchy', 'department', 'user', 'responsible', 'is_active',
                  'repentance_date_from', 'repentance_date_to', 'group']


class PartnerFilterByDateAge(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        age_gt = request.query_params.get('age_gt')
        age_lt = request.query_params.get('age_lt')

        age_reg = re.compile('(\d+\s*(year|month|day))')
        try:
            age_gt = age_reg.search(age_gt).group(0) if age_gt else None
        except:
            age_gt = None
        try:
            age_lt = age_reg.search(age_lt).group(0) if age_lt else None
        except:
            age_lt = None

        if age_gt and age_lt:
            return queryset.extra(where=["age(date) BETWEEN INTERVAL %s AND interval %s"], params=[age_gt, age_lt])
        elif age_gt:
            return queryset.extra(where=["age(date) >= INTERVAL %s"], params=[age_gt])
        elif age_lt:
            return queryset.extra(where=["age(date) <= INTERVAL %s"], params=[age_lt])

        return queryset


class DealsDuplicatesFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('check_duplicates'):
            query = """
                SELECT
                array_agg(d.id) c,
                p.id,
                d.value,
                to_char(d.date_created, 'YYYY.MM')
                FROM partnership_deal d
                JOIN partnership_partnership p on d.partnership_id = p.id
                GROUP BY p.id, d.value, to_char(d.date_created, 'YYYY.MM')
                HAVING count(*) > 1
                ORDER BY count(*) DESC;
            """

            with connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()

            deal_ids = []
            for value in data:
                for _id in value[0]:
                    deal_ids.append(_id)
            return queryset.filter(id__in=deal_ids).order_by('partnership_id')

        return queryset
