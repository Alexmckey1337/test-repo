# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser as User
from account.serializers import NewUserSerializer
from .models import Summit, SummitAnket, SummitType, SummitAnketNote, SummitLesson, AnketEmail


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


class AnketEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnketEmail
        fields = ('id', 'created_at')


class SummitAnketSerializer(serializers.HyperlinkedModelSerializer):
    user = NewUserSerializer()
    emails = AnketEmailSerializer(many=True, read_only=True)

    class Meta:
        model = SummitAnket
        fields = ('id', 'user', 'code', 'value', 'description',
                  'is_member',
                  'emails',
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
        fields = ('id', 'start_date', 'end_date', 'title', 'description', 'lessons', 'club_name')


class SummitTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SummitType
        fields = ('id', 'title', 'image')


class SummitForAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'description')


class SummitTypeForAppSerializer(serializers.ModelSerializer):
    summits = SummitForAppSerializer(many=True, read_only=True)

    class Meta:
        model = SummitType
        fields = ('title', 'summits')


class UserForAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'middle_name',
                  'phone_number', 'country', 'region', 'city', 'district', 'address', 'image_source')


class SummitAnketForAppSerializer(serializers.ModelSerializer):
    user = UserForAppSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'user', 'code')


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
