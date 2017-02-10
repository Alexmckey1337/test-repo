import django_filters
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import get_object_or_404

from account.models import CustomUser
from group.models import Church, HomeGroup
from hierarchy.models import Department


class ChurchAllUserFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        church_id = view.kwargs.get('pk')
        church = get_object_or_404(Church, pk=church_id)
        queryset = queryset.filter(Q(churches=church) | Q(home_groups__in=church.home_group.all()))

        return queryset


class HomeGroupFilter(django_filters.FilterSet):
    church = django_filters.ModelChoiceFilter(name='church', queryset=Church.objects.all())
    leader = django_filters.ModelChoiceFilter(name='leader', queryset=CustomUser.objects.filter(
        hierarchy__level__gt=0))

    class Meta:
        model = HomeGroup
        fields = ['church', 'leader', 'title', 'city', 'phone_number', 'website']


class ChurchFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(name='department', queryset=Department.objects.all())
    pastor = django_filters.ModelChoiceFilter(name='pastor', queryset=CustomUser.objects.filter(
        hierarchy__level__gt=1))

    class Meta:
        model = Church
        fields = ['department', 'pastor', 'title', 'country', 'city', 'is_open', 'phone_number']
