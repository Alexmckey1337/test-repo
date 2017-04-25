import django_filters
from rest_framework import filters
from account.models import CustomUser
from event.models import ChurchReport, Meeting


class CommonMeetingFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date", lookup_type='gte')
    to_date = django_filters.DateFilter(name="date", lookup_type='lte')

    class Meta:
        fields = ('status', 'from_date', 'to_date')


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


class MeetingFilterByDepartment(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        department_id = request.query_params.get('department_id')
        if department_id:
            return queryset.filter(home_group__church__department__id=department_id)

        return queryset
