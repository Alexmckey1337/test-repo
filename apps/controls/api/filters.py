import django_filters
from rest_framework import filters

from apps.summit.models import Summit
from common.filters import BaseFilterMasterTree


class SummitPanelDateFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(name='start_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(name='end_date', lookup_expr='lte')

    class Meta:
        model = Summit
        fields = ('status', 'type', 'start_date', 'end_date')


class DbAccessFilterByDepartments(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        departments = request.query_params.get('departments')
        if departments:
            departments = [int(x) for x in departments if x.isdigit()]
            queryset = queryset.filter(departments__in=departments)

        return queryset


class FilterMasterTree(BaseFilterMasterTree):
    include_self_master = False
