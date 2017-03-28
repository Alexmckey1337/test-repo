import operator

import django_filters
from django.db import models
from django.utils import six
from rest_framework.filters import BaseFilterBackend, FilterSet

from partnership.models import Deal
from payment.models import Payment

if six.PY3:
    from functools import reduce


class PaymentFilterByPurpose(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        purpose = request.query_params.getlist('purpose', None)
        if not purpose:
            return queryset
        return queryset.filter(content_type__model__in=purpose)


class PaymentFilter(FilterSet):
    sum_to = django_filters.NumberFilter(name="sum", lookup_type='lte')
    sum_from = django_filters.NumberFilter(name="sum", lookup_type='gte')
    eff_sum_to = django_filters.NumberFilter(name="effective_sum", lookup_type='lte')
    eff_sum_from = django_filters.NumberFilter(name="effective_sum", lookup_type='gte')
    create_to = django_filters.DateFilter(name="created_at", lookup_type='lte')
    create_from = django_filters.DateFilter(name="created_at", lookup_type='gte')
    sent_to = django_filters.DateFilter(name="sent_date", lookup_type='lte')
    sent_from = django_filters.DateFilter(name="sent_date", lookup_type='gte')

    class Meta:
        model = Payment
        fields = ['sum_from', 'sum_to', 'eff_sum_from', 'eff_sum_to', 'currency_sum',
                  'currency_rate', 'create_from', 'create_to', 'sent_from', 'sent_to', 'manager']


class FilterByDealFIO(BaseFilterBackend):
    include_self_master = False

    def get_deals(self, request):
        return Deal.objects.for_user(request.user)

    def filter_queryset(self, request, queryset, view):
        purpose_fio = request.query_params.get('search_purpose_fio', None)
        if not purpose_fio:
            return queryset

        orm_lookups = [
            'partnership__user__first_name__icontains',
            'partnership__user__last_name__icontains',
            'partnership__user__middle_name__icontains',
            'partnership__user__search_name__icontains']

        deals = self.get_deals(request)
        for search_term in purpose_fio.replace(',', ' ').split():
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups]
            deals = deals.filter(reduce(operator.or_, queries))

        deal_ids = deals.values_list('id', flat=True)

        return queryset.filter(content_type__model='deal', object_id__in=deal_ids)
