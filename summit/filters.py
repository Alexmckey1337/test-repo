from datetime import datetime

import django_filters
import rest_framework_filters as filters_new
from django.db.models import OuterRef, Subquery
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

from account.filters import FilterMasterTreeWithSelf
from account.models import CustomUser
from hierarchy.models import Hierarchy, Department
from summit.models import Summit, SummitAnket, SummitAttend


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


class HasPhoto(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Return a filtered queryset.
        """
        params = request.query_params
        has_photo = params.get('has_photo', None)
        if has_photo in ('true', 'false'):
            if has_photo == 'false':
                return queryset.filter(user__image='')
            return queryset.exclude(user__image='')
        return queryset


class FilterByTime(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Return a filtered queryset.
        """
        params = request.query_params
        attend_from = params.get('attend_from', None)
        attend_to = params.get('attend_to', None)
        d = view.filter_date
        if attend_from and attend_to:
            attends = SummitAttend.objects.filter(
                Q(date=d) &
                (Q(time__range=(attend_from, attend_to)) |
                 (Q(time__isnull=True) & Q(created_at__time__range=(attend_from, attend_to)))),
                anket=OuterRef('pk'))
        elif attend_from:
            attends = SummitAttend.objects.filter(
                Q(date=d) &
                (Q(time__gte=attend_from) |
                 (Q(time__isnull=True) & Q(created_at__time__gte=attend_from))),
                anket=OuterRef('pk'))
        elif attend_to:
            attends = SummitAttend.objects.filter(
                Q(date=d) &
                (Q(time__lte=attend_to) |
                 (Q(time__isnull=True) & Q(created_at__time__lte=attend_to))),
                anket=OuterRef('pk'))
        else:
            return queryset
        return queryset.filter(pk__in=Subquery(attends.values('anket_id')[:1]))


class ProductFilter(django_filters.FilterSet):
    min_id = django_filters.NumberFilter(name="id", lookup_expr='gte')
    max_id = django_filters.NumberFilter(name="id", lookup_expr='lte')

    class Meta:
        model = SummitAnket
        fields = ['summit', 'min_id', 'max_id']


class SummitUnregisterFilter(filters_new.FilterSet):
    summit_id = filters_new.CharFilter(name="summit_profiles__summit__id", exclude=True)

    class Meta:
        model = CustomUser
        fields = ['summit_id']


class ProfileFilter(django_filters.FilterSet):
    hierarchy = django_filters.ModelChoiceFilter(name='hierarchy', queryset=Hierarchy.objects.all())
    master = django_filters.ModelMultipleChoiceFilter(name="master", queryset=CustomUser.objects.all())
    department = django_filters.ModelChoiceFilter(name="departments", queryset=Department.objects.all())

    class Meta:
        model = SummitAnket
        fields = ['master', 'hierarchy', 'department', 'ticket_status']


class FilterProfileMasterTreeWithSelf(FilterMasterTreeWithSelf):
    user_field_prefix = 'user__'


class FilterBySummitAttend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_visited = request.query_params.get('is_visited', 0)
        if not is_visited:
            return queryset

        date_today = datetime.now().strftime("%Y-%m-%d")
        from_date = request.query_params.get('from_date', date_today)
        to_date = request.query_params.get('to_date', date_today)

        if int(is_visited) == 1:
            queryset = queryset.filter(attends__date__range=[from_date, to_date])
        elif int(is_visited) == 2:
            queryset = queryset.exclude(attends__date__range=[from_date, to_date])

        return queryset


class FilterBySummitAttendByDate(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        attended = request.query_params.get('attended', '')

        if attended.upper() in ('TRUE', 'T', 'YES', 'Y', '1'):
            return queryset.filter(attended__isnull=False)
        elif attended.upper() in ('FALSE', 'F', 'NO', 'N', '0'):
            return queryset.filter(attended__isnull=True)

        return queryset


class FilterByElecTicketStatus(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        e_ticket = request.query_params.get('e_ticket', None)
        if e_ticket in ('true', 'false'):
            if e_ticket == 'false':
                return queryset.filter(Q(status__reg_code_requested=None) | Q(status__reg_code_requested=False))
            return queryset.filter(status__reg_code_requested=True)
        return queryset
