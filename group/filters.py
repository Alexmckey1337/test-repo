import django_filters
from django.core.exceptions import ObjectDoesNotExist
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
        queryset = queryset.filter(
            Q(churches=church) | Q(home_groups__in=church.home_group.all()))

        return queryset


class HomeGroupFilter(django_filters.FilterSet):
    church = django_filters.ModelChoiceFilter(name='church', queryset=Church.objects.all())
    leader = django_filters.ModelChoiceFilter(name='leader', queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())

    class Meta:
        model = HomeGroup
        fields = ('church', 'leader', 'opening_date', 'city')


class HomeGroupsDepartmentFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        department = request.query_params.get('department')
        if department:
            queryset = queryset.filter(church__department=department)

        return queryset


class ChurchFilter(django_filters.FilterSet):
    department = django_filters.ModelMultipleChoiceFilter(name="department",
                                                          queryset=Department.objects.all())

    pastor = django_filters.ModelChoiceFilter(name='pastor', queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct())

    class Meta:
        model = Church
        fields = ('department', 'pastor', 'is_open', 'opening_date', 'country',
                  'city')


class CommonGroupMasterTreeFilter(BaseFilterBackend):
    level = None
    search = None

    def filter_queryset(self, request, queryset, view):
        master_id = request.query_params.get('master_tree', None)
        try:
            master = CustomUser.objects.get(pk=master_id)
        except ObjectDoesNotExist:
            return queryset

        if master.is_leaf_node():
            return queryset.none()

        master_tree_id = master.tree_id
        master_left = master.lft
        master_right = master.rght

        users = CustomUser.objects.filter(hierarchy__level__gte=self.level).filter(
            tree_id=master_tree_id, lft__gte=master_left, rght__lte=master_right)

        return queryset.filter(**{self.search: [user.id for user in users]})


class FilterChurchMasterTree(CommonGroupMasterTreeFilter):
    level = 2
    search = 'pastor_id__in'


class FilterHomeGroupMasterTree(CommonGroupMasterTreeFilter):
    level = 1
    search = 'leader_id__in'
