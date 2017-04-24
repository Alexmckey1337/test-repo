import django_filters

from account.models import CustomUser
from event.models import ChurchReport, Meeting
from hierarchy.models import Department

COMMON_MEETING_FIELDS = ('department', 'status', 'from_date', 'to_date')


class CommonMeetingFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date", lookup_type='gte')
    to_date = django_filters.DateFilter(name="date", lookup_type='lte')

    department = django_filters.ModelMultipleChoiceFilter(
        name="department", queryset=Department.objects.all())


class ChurchReportFilter(CommonMeetingFilter):
    pastor = django_filters.ModelChoiceFilter(name='pastor', queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct())

    class Meta:
        model = ChurchReport
        fields = ('church', 'pastor') + COMMON_MEETING_FIELDS


class MeetingFilter(CommonMeetingFilter):
    owner = django_filters.ModelChoiceFilter(name='owner', queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())

    class Meta:
        model = Meeting
        fields = ('home_group', 'owner') + COMMON_MEETING_FIELDS
