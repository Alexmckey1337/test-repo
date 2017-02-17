# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers
from .models import Event, Participation, EventType, EventAnket
from .models import Meeting, MeetingAttend, MeetingType, ChurchReport
from account.models import CustomUser
from group.models import HomeGroup, Church
from group.serializers import LeaderNameSerializer, PastorNameSerializer, ChurchNameSerializer
from django.utils.translation import ugettext as _


class MeetingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingType
        fields = ('id', 'name')


class HomeGroupNameSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='get_title', read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'title')


class MeetingSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())
    visitors_absent = serializers.IntegerField(read_only=True)
    visitors_attended = serializers.IntegerField(read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'date', 'home_group', 'owner',  'type', 'visitors_attended',
                  'visitors_absent', 'total_sum')


class MeetingListSerializer(MeetingSerializer):
    home_group = HomeGroupNameSerializer()
    type = MeetingTypeSerializer()
    owner = LeaderNameSerializer()


class MeetingAttendSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingAttend
        fields = ('user', 'attended', 'note')


class MeetingDetailSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())
    attends = MeetingAttendSerializer(many=True)

    class Meta:
        model = Meeting
        fields = ('id', 'owner', 'type', 'date', 'total_sum', 'attends')


class ChurchReportSerializer(serializers.ModelSerializer):
    pastor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct())
    church = serializers.PrimaryKeyRelatedField(queryset=Church.objects.all())

    class Meta:
        model = ChurchReport
        fields = ('id', 'date', 'pastor', 'church', 'count_people', 'new_people', 'count_repentance',
                  'tithe', 'donations', 'currency_donations', 'transfer_payments', 'pastor_tithe')


class ChurchReportListSerializer(ChurchReportSerializer):
    pastor = PastorNameSerializer()
    church = ChurchNameSerializer()























class EventTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventType
        fields = ('url', 'id', 'title', 'image', 'event_count', 'last_event_date',)


class EventAnketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventAnket
        fields = ('url', 'id', 'user', 'participations', 'events',)


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'event_type', 'from_date', 'to_date', 'time', 'title',)


class ParticipationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Participation
        fields = ('id', 'check', 'value', 'uid', 'hierarchy_chain', 'has_disciples', 'fields',)
