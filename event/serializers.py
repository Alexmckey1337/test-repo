# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Event, Participation, EventType, EventAnket
from .models import Meeting, MeetingAttend, MeetingType
from account.models import CustomUser


class MeetingAttendedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingAttend
        fields = ('id', 'attended', 'note', 'user', 'meeting')


class MeetingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname', 'spiritual_level', 'phone_number', 'attends')


class MeetingUserAttendsSerializer(MeetingUserSerializer):
    attends = MeetingAttendedSerializer(many=True)


class MeetingSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(hierarchy__level=1))
    visitors = MeetingUserAttendsSerializer(many=True)

    class Meta:
        model = Meeting
        fields = ('id', 'owner', 'type', 'date', 'total_sum', 'visitors')

    def create(self, validated_data):
        visitors = validated_data.pop('visitors')
        meeting = Meeting.objects.create(**validated_data)
        for visitor in visitors:
            for attended in visitor['attends']:
                MeetingAttend.objects.create(meeting_id=meeting.id, **attended)
        return meeting













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
