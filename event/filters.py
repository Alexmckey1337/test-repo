import django_filters
from rest_framework import filters
from account.models import CustomUser
from event.models import ChurchReport, Meeting
from common.filters import BaseFilterMasterTree
from django.db.models import Q


class CommonMeetingFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date", lookup_expr='gte')
    to_date = django_filters.DateFilter(name="date", lookup_expr='lte')

    class Meta:
        fields = ('status', 'date', 'from_date', 'to_date')


class MeetingFilter(CommonMeetingFilter):
    owner = django_filters.ModelChoiceFilter(name='owner', queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())

    class Meta(CommonMeetingFilter.Meta):
        model = Meeting
        fields = CommonMeetingFilter.Meta.fields + ('home_group', 'owner', 'type')


class ChurchReportFilter(CommonMeetingFilter):
    pastor = django_filters.ModelChoiceFilter(name='pastor', queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct())

    class Meta(CommonMeetingFilter.Meta):
        model = ChurchReport
        fields = CommonMeetingFilter.Meta.fields + ('church', 'pastor')


class MeetingCustomFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        department = request.query_params.get('department')
        church = request.query_params.get('church')

        if department:
            queryset = queryset.filter(home_group__church__department__id=department)

        if church:
            queryset = queryset.filter(home_group__church__id=church)

        return queryset


class ChurchReportDepartmentFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        department = request.query_params.get('department')
        if department:
            queryset = queryset.filter(church__department__id=department)

        return queryset


class MeetingFilterByMaster(BaseFilterMasterTree):
    include_self_master = True
    user_field_prefix = 'owner__'


class ChurchReportFilterByMaster(BaseFilterMasterTree):
    include_self_master = True
    user_field_prefix = 'pastor__'


class EventSummaryMasterFilter(MeetingFilterByMaster):
    include_self_master = True
    user_field_prefix = None


class EventSummaryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        responsible_id = request.query_params.get('responsible_id')
        if responsible_id:
            queryset = queryset.filter(master__id=responsible_id)

        department_id = request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(departments__id__in=department_id)

        church_id = request.query_params.get('church_id')
        if church_id:
            queryset = queryset.filter(Q(cchurch__id=church_id) | Q(hhome_group__church__id=church_id))

        return queryset
