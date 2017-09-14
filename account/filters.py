import django_filters
from django.utils.translation import ugettext_lazy as _

from account.models import CustomUser as User
from common.filters import BaseFilterByBirthday, BaseFilterMasterTree
from hierarchy.models import Hierarchy, Department
from summit.models import Summit
from rest_framework import filters


class FilterByUserBirthday(BaseFilterByBirthday):
    born_date_field = 'born_date'


class FilterByUserRepentance(BaseFilterByBirthday):
    born_date_field = 'repentance_date'


class FilterMasterTree(BaseFilterMasterTree):
    include_self_master = False


class FilterMasterTreeWithSelf(BaseFilterMasterTree):
    include_self_master = True


class FilterDashboardMasterTreeWithSelf(FilterMasterTreeWithSelf):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_staff:
            return queryset
        return super(FilterDashboardMasterTreeWithSelf, self).filter_queryset(request, queryset, view)


class UserFilter(django_filters.FilterSet):
    hierarchy = django_filters.ModelChoiceFilter(name='hierarchy', queryset=Hierarchy.objects.all(),
                                                 help_text=_('Hierarchy'))
    master = django_filters.ModelMultipleChoiceFilter(name="master", queryset=User.objects.all(),
                                                      help_text=_('Master'))
    department = django_filters.ModelChoiceFilter(name="departments", queryset=Department.objects.all(),
                                                  help_text=_('Department'))
    repentance_date_from = django_filters.DateFilter(name='repentance_date', lookup_expr='gte')
    repentance_date_to = django_filters.DateFilter(name='repentance_date', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['master', 'hierarchy', 'department', 'repentance_date_from', 'repentance_date_to']


class ShortUserFilter(django_filters.FilterSet):
    level_gt = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='gt')
    level_gte = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='gte')
    level_lt = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='lt')
    level_lte = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='lte')
    department = django_filters.ModelMultipleChoiceFilter(name="departments", queryset=Department.objects.all())
    summit = django_filters.ModelChoiceFilter(name="summit_profiles__summit_id", queryset=Summit.objects.all())

    class Meta:
        model = User
        fields = ['level_gt', 'level_gte', 'level_lt', 'level_lte', 'department', 'master', 'summit']


class UserIsPartnershipFilter(filters.DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_partner = request.query_params.get('is_partner')
        if is_partner not in ['true', 'false']:
            return queryset
        if is_partner == 'true':
            return queryset.filter(partnership__isnull=False)
        if is_partner == 'false':
            return queryset.filter(partnership__isnull=True)

        return queryset


from django.db.models import Q


class UserChurchFilter(filters.DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        church_id = request.query_params.get('church_id')
        if not church_id:
            return queryset
        return queryset.filter(Q(cchurch_id=church_id) | Q(hhome_group__church_id=church_id))
