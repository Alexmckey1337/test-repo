from models import UserReport, DayReport, MonthReport, YearReport
from rest_framework import serializers


class UserReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserReport
        fields = ('url', 'id', 'user', 'date', 'count', 'event', )


class DayReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DayReport
        fields = ('url', 'id', 'date', 'count', 'event', 'department')


class MonthReportSerializer(serializers.HyperlinkedModelSerializer):
    count = serializers.IntegerField()
    class Meta:
        model = MonthReport
        fields = ('url', 'id', 'date', 'count', 'department')


class YearReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = YearReport
        fields = ('url', 'id', 'date', 'count', 'department')
