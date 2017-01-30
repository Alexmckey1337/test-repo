# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Event, Participation, EventType, EventAnket
from .models import Meeting, MeetingAttend
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


class MeetingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname', 'spiritual_level', 'phone_number')


class MeetingAttendSerializer(serializers.ModelSerializer):
    user = MeetingUserSerializer()

    class Meta:
        models = MeetingAttend
        fields = ('user', 'attended', 'note')


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ('id', 'owner', 'type', 'date', 'total_sum',)
