import django_filters
from rest_framework import filters

from account.models import CustomUser
from common.filters import BaseFilterByBirthday, BaseFilterMasterTree
from hierarchy.models import Hierarchy, Department
from partnership.models import Deal, Partnership


class DateFilter(filters.FilterSet):
    to_date = django_filters.DateFilter(name="date_created", lookup_type='lte')
    from_date = django_filters.DateFilter(name="date_created", lookup_type='gte')

    class Meta:
        model = Deal
        fields = ['partnership__responsible__user',
                  'partnership__user', 'value', 'date_created', 'date',
                  'expired', 'done', 'to_date', 'from_date', ]


class FilterByPartnerBirthday(BaseFilterByBirthday):
    born_date_field = 'user__born_date'


class FilterPartnerMasterTreeWithSelf(BaseFilterMasterTree):
    include_self_master = True
    user_field_prefix = 'user__'


class PartnerUserFilter(django_filters.FilterSet):
    hierarchy = django_filters.ModelChoiceFilter(name='user__hierarchy', queryset=Hierarchy.objects.all())
    master = django_filters.ModelMultipleChoiceFilter(name="user__master", queryset=CustomUser.objects.all())
    department = django_filters.ModelChoiceFilter(name="user__departments", queryset=Department.objects.all())

    class Meta:
        model = Partnership
        fields = ['master', 'hierarchy', 'department']
