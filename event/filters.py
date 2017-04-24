import django_filters

from account.models import CustomUser
from hierarchy.models import Department
from event.models import ChurchReport, Meeting


class CommonMeetingFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(name="date", lookup_type='gte')
    to_date = django_filters.DateFilter(name="date", lookup_type='lte')

    department = django_filters.ModelMultipleChoiceFilter(
        name="department", queryset=Department.objects.all())

    class Meta:
        fields = ('department', 'status', 'from_date', 'to_date')


class ChurchReportFilter(CommonMeetingFilter):
    pastor = django_filters.ModelChoiceFilter(name='pastor', queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct())

    class Meta(CommonMeetingFilter.Meta):
        model = ChurchReport
        fields = CommonMeetingFilter.Meta.fields + ('church', 'pastor')


class MeetingFilter(CommonMeetingFilter):
    owner = django_filters.ModelChoiceFilter(name='owner', queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())

    class Meta(CommonMeetingFilter.Meta):
        model = Meeting
        fields = CommonMeetingFilter.Meta.fields + ('home_group', 'owner')
