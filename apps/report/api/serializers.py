from rest_framework import serializers

from apps.report.models import UserReport, WeekReport, MonthReport, YearReport


class UserReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserReport
        fields = ('url', 'id',)


class WeekReportSerializer(serializers.HyperlinkedModelSerializer):
    week = serializers.StringRelatedField()

    class Meta:
        model = WeekReport
        fields = ('id', 'uid', 'mid', 'fullname', 'week', 'from_date',
                  'to_date', 'home_count', 'home_value',
                  'night_count', 'service_count',
                  'service_coming_count', 'service_repentance_count',
                  'home_as_leader_count', 'home_as_leader_value',
                  'night_as_leader_count', 'service_as_leader_count',
                  'service_as_leader_coming_count', 'service_as_leader_repentance_count',)


class MonthReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonthReport
        fields = ('id', 'uid', 'mid', 'fullname', 'date',
                  'home_count', 'home_value',
                  'night_count', 'service_count',
                  'service_coming_count', 'service_repentance_count',
                  'home_as_leader_count', 'home_as_leader_value',
                  'night_as_leader_count', 'service_as_leader_count',
                  'service_as_leader_coming_count', 'service_as_leader_repentance_count',)


class YearReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = YearReport
        fields = ('id', 'uid', 'mid', 'fullname', 'date',
                  'home_count', 'home_value',
                  'night_count', 'service_count',
                  'service_coming_count', 'service_repentance_count',
                  'home_as_leader_count', 'home_as_leader_value',
                  'night_as_leader_count', 'service_as_leader_count',
                  'service_as_leader_coming_count', 'service_as_leader_repentance_count',)
