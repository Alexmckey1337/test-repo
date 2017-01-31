# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Event, Participation, EventType, EventAnket
from .models import Meeting, MeetingAttend, MeetingType
from account.models import CustomUser


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


class MeetingAttendSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingAttend
        fields = ('attended', 'note')


class UserMeetingSerializer(serializers.ModelSerializer):
    attends = MeetingAttendSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'fullname', 'spiritual_level', 'phone_number', 'attends')


class MeetingSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(hierarchy__level=1))
    visitors = UserMeetingSerializer(many=True,)

    class Meta:
        model = Meeting
        fields = ('id', 'owner', 'type', 'date', 'total_sum', 'visitors')
