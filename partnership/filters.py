import django_filters

from account.models import CustomUser
from common.filters import BaseFilterByBirthday, BaseFilterMasterTree
from hierarchy.models import Hierarchy, Department
from partnership.models import Deal, Partnership
from rest_framework import filters


class DateAndValueFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date_created", lookup_expr='gte')
    to_date = django_filters.DateFilter(name="date_created", lookup_expr='lte')
    from_value = django_filters.NumberFilter(name="value", lookup_expr='gte')
    to_value = django_filters.NumberFilter(name="value", lookup_expr='lte')

    class Meta:
        model = Deal
        fields = ['partnership__responsible__user', 'currency_id',
                  'partnership__user', 'value', 'date_created', 'date',
                  'expired', 'done', 'to_date', 'from_date', 'from_value', 'to_value']


class DealFilterByPaymentStatus(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        payment_status = request.query_params.get('payment_status')
        type = request.query_params.get('type')

        if payment_status:
            return queryset.filter(payment_status=payment_status)

        if type:
            return queryset.filter(type=type)

        return queryset


class FilterByPartnerBirthday(BaseFilterByBirthday):
    born_date_field = 'user__born_date'


class FilterPartnerMasterTreeWithSelf(BaseFilterMasterTree):
    include_self_master = True
    user_field_prefix = 'user__'


class PartnerUserFilter(django_filters.FilterSet):
    hierarchy = django_filters.ModelChoiceFilter(name='user__hierarchy', queryset=Hierarchy.objects.all())
    master = django_filters.ModelMultipleChoiceFilter(name="user__master", queryset=CustomUser.objects.all())
    department = django_filters.ModelChoiceFilter(name="user__departments", queryset=Department.objects.all())
    is_active = django_filters.BooleanFilter(name='is_active')
    value_to = django_filters.NumberFilter(name="value", lookup_expr='lte')
    value_from = django_filters.NumberFilter(name="value", lookup_expr='gte')
    repentance_date_from = django_filters.DateFilter(name='user__repentance_date', lookup_expr='gte')
    repentance_date_to = django_filters.DateFilter(name='user__repentance_date', lookup_expr='lte')

    class Meta:
        model = Partnership
        fields = ['master', 'hierarchy', 'department', 'user', 'responsible__user', 'responsible', 'is_active',
                  'repentance_date_from', 'repentance_date_to']
