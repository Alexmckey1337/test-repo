import django_filters

from account.models import CustomUser as User
from common.filters import BaseFilterByBirthday, BaseFilterMasterTree
from hierarchy.models import Hierarchy, Department


class FilterByUserBirthday(BaseFilterByBirthday):
    born_date_field = 'born_date'


class FilterMasterTree(BaseFilterMasterTree):
    include_self_master = False


class FilterMasterTreeWithSelf(BaseFilterMasterTree):
    include_self_master = True


class UserFilter(django_filters.FilterSet):
    hierarchy = django_filters.ModelChoiceFilter(name='hierarchy', queryset=Hierarchy.objects.all())
    master = django_filters.ModelMultipleChoiceFilter(name="master", queryset=User.objects.all())
    department = django_filters.ModelChoiceFilter(name="departments", queryset=Department.objects.all())

    class Meta:
        model = User
        fields = ['master', 'hierarchy', 'department']


class ShortUserFilter(django_filters.FilterSet):
    level_gt = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='gt')
    level_gte = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='gte')
    level_lt = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='lt')
    level_lte = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='lte')
    department = django_filters.ModelMultipleChoiceFilter(name="departments", queryset=Department.objects.all())

    class Meta:
        model = User
        fields = ['level_gt', 'level_gte', 'level_lt', 'level_lte', 'department']
