# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser as User
from account.serializers import NewUserSerializer
from .models import Summit, SummitAnket, SummitType, SummitAnketNote, SummitLesson


class SummitAnketNoteSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = SummitAnketNote
        fields = ('summit_anket', 'text', 'owner', 'date_created', 'owner_name')
        read_only_fields = ('owner', 'date_created', 'id')
        extra_kwargs = {'summit_anket': {'write_only': True}}


class SummitAnketOldSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SummitAnket
        fields = ('info', 'common', 'code',)


class SummitAnketSerializer(serializers.HyperlinkedModelSerializer):
    user = NewUserSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'user', 'code', 'value', 'description',
                  'is_member',
                  'visited')


class SummitAnketWithNotesSerializer(serializers.ModelSerializer):
    notes = SummitAnketNoteSerializer(many=True, read_only=True)

    class Meta:
        model = SummitAnket
        fields = ('info', 'common', 'code', 'notes')


class SummitSerializer(serializers.HyperlinkedModelSerializer):
    lessons = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'title', 'description', 'lessons')


class SummitTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SummitType
        fields = ('id', 'title', 'image')


class SummitUnregisterUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'city', 'fullname', 'country', 'master_short_fullname')


class SummitLessonSerializer(serializers.ModelSerializer):
    viewers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = SummitLesson
        fields = ('summit', 'name', 'viewers')
        # extra_kwargs = {'viewers': {'required': False}}
