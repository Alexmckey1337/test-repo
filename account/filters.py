import operator
from datetime import datetime, timedelta

import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.filters import BaseFilterBackend

from account.models import CustomUser as User, CustomUser
from hierarchy.models import Hierarchy, Department


class FilterByBirthday(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        from functools import reduce
        params = request.query_params
        from_date = params.get('from_date', None)
        to_date = params.get('to_date', None)
        if from_date is None or to_date is None:
            return queryset
        if from_date > to_date:
            raise exceptions.ValidationError(detail=_('Некоректный временной интервал'))
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
        monthdays = [(from_date.month, from_date.day)]
        while from_date <= to_date:
            monthdays.append((from_date.month, from_date.day))
            from_date += timedelta(days=1)
        monthdays = (dict(zip(("born_date__month", "born_date__day"), t)) for t in monthdays)
        query = reduce(operator.or_, (Q(**d) for d in monthdays))
        return queryset.filter(query)


class FilterMasterTree(BaseFilterBackend):
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

        return queryset.exclude(pk=master).filter(tree_id=master_tree_id, lft__gte=master_left, rght__lte=master_right)


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
