import django_filters
from apps.summit.models import Summit


class SummitPanelDateFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(name='start_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(name='end_date', lookup_expr='lte')

    class Meta:
        model = Summit
        fields = ('status', 'type', 'start_date', 'end_date')
