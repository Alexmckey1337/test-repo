import django_filters
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework

from apps.account.models import CustomUser as User
from common.filters import BaseFilterByBirthday, BaseFilterMasterTree
from apps.hierarchy.models import Hierarchy, Department
from apps.summit.models import Summit


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
        fields = ['master', 'hierarchy', 'department', 'repentance_date_from', 'repentance_date_to',
                  'spiritual_level', 'is_dead', 'is_stable']


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


class UserIsPartnershipFilter(rest_framework.DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_partner = request.query_params.get('is_partner')
        if is_partner not in ['true', 'false']:
            return queryset
        if is_partner == 'true':
            return queryset.filter(partners__isnull=False)
        if is_partner == 'false':
            return queryset.filter(partners__isnull=True)
        return queryset


class UserChurchFilter(rest_framework.DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        church_id = request.query_params.get('church_id')

        if church_id in ['any', 'nothing']:
            if church_id == 'any':
                return queryset.filter(Q(cchurch__isnull=False) | Q(hhome_group__church__isnull=False))
            else:
                return queryset.filter(Q(cchurch__isnull=True) & Q(hhome_group__church__isnull=True))

        if isinstance(church_id, int):
            return queryset.filter(Q(cchurch_id=church_id) | Q(hhome_group__church_id=church_id))

        return queryset


class UserHomeGroupFilter(rest_framework.DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        home_group_id = request.query_params.get('home_group_id')

        if home_group_id in ['any', 'nothing']:
            if home_group_id == 'any':
                return queryset.filter(hhome_group__isnull=False)
            else:
                return queryset.filter(hhome_group__isnull=True)

        return queryset


class UserHGLeadersFilter(rest_framework.DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user_type = request.query_params.get('user_type')

        if user_type == 'leaders':
            return queryset.filter(home_group__leader__isnull=False).distinct()

        return queryset
