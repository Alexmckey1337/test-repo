# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser as User
from account.serializers import UserTableSerializer, UserShortSerializer
from .models import Summit, SummitAnket, SummitType, SummitAnketNote, SummitLesson, AnketEmail, SummitTicket


class SummitAnketNoteSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = SummitAnketNote
        fields = ('summit_anket', 'text', 'owner', 'date_created', 'owner_name')
        read_only_fields = ('owner', 'date_created', 'id')
        extra_kwargs = {'summit_anket': {'write_only': True}}


class AnketEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnketEmail
        fields = ('id', 'created_at')


class SummitAnketSerializer(serializers.HyperlinkedModelSerializer):
    user = UserTableSerializer()
    emails = AnketEmailSerializer(many=True, read_only=True)
    total_sum = serializers.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        model = SummitAnket
        fields = ('id', 'user', 'code', 'description',
                  'emails',
                  'visited',

                  'is_member',
                  # 'is_full_paid',
                  'total_sum',
                  )


class SummitAnketShortSerializer(serializers.HyperlinkedModelSerializer):
    user = UserTableSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'user', 'code', 'description', 'visited')


class SummitAnketForSelectSerializer(serializers.HyperlinkedModelSerializer):
    user = UserShortSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'role', 'user')


class UserWithLinkSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'fullname', 'link')


class SummitAnketForTicketSerializer(serializers.HyperlinkedModelSerializer):
    user = UserWithLinkSerializer()
    is_active = serializers.BooleanField()

    class Meta:
        model = SummitAnket
        fields = ('id', 'code', 'user', 'is_active')


class SummitShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'title', 'description')


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


class SummitLessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummitLesson
        fields = ('summit', 'name')


# UNUSED


class SummitSerializer(serializers.HyperlinkedModelSerializer):
    lessons = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'title', 'description', 'lessons', 'club_name',
                  'full_cost', 'special_cost')


class SummitTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SummitType
        fields = ('id', 'title', 'image')


class SummitAnketWithNotesSerializer(serializers.ModelSerializer):
    notes = SummitAnketNoteSerializer(many=True, read_only=True)

    class Meta:
        model = SummitAnket
        fields = ('code', 'notes')


# FOR APP


class SummitTicketSerializer(serializers.ModelSerializer):
    summit_type = serializers.IntegerField(source='summit.type.id')
    summit = SummitSerializer()
    owner = UserShortSerializer()

    class Meta:
        model = SummitTicket
        fields = ('id', 'title', 'summit', 'summit_type', 'owner', 'attachment', 'status', 'get_status_display')


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
        fields = ('id', 'user', 'code', 'value', 'is_member')
