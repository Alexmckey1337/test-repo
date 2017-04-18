import django_filters
import rest_framework_filters as filters_new
from rest_framework.filters import BaseFilterBackend

from account.models import CustomUser
from summit.models import Summit, SummitAnket


class FilterByClub(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Return a filtered queryset.
        """
        params = request.query_params
        summit_id = params.get('summit')
        is_member = params.get('is_member', None)
        if summit_id and is_member in ('true', 'false'):
            is_member = True if is_member == 'true' else False
            summit_type = Summit.objects.get(id=summit_id).type
            users = summit_type.summits.filter(ankets__visited=True).values_list('ankets__user', flat=True)
            if is_member:
                return queryset.filter(user__id__in=set(users))
            return queryset.exclude(user__id__in=set(users))
        return queryset


class ProductFilter(django_filters.FilterSet):
    min_id = django_filters.NumberFilter(name="id", lookup_expr='gte')
    max_id = django_filters.NumberFilter(name="id", lookup_expr='lte')

    class Meta:
        model = SummitAnket
        fields = ['summit', 'min_id', 'max_id']


class SummitUnregisterFilter(filters_new.FilterSet):
    summit_id = filters_new.CharFilter(name="summit_ankets__summit__id", exclude=True)

    class Meta:
        model = CustomUser
        fields = ['summit_id']
