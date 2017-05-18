# -*- coding: utf-8
from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import serializers

from account.models import CustomUser as User
from account.serializers import UserTableSerializer, UserShortSerializer
from common.fields import ListCharField, ReadOnlyChoiceWithKeyField
from hierarchy.serializers import HierarchySerializer
from .models import (Summit, SummitAnket, SummitType, SummitAnketNote, SummitLesson, AnketEmail,
                     SummitTicket, SummitVisitorLocation, SummitEventTable)


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
    user_id = serializers.IntegerField(source='user.user_ptr_id')
    emails = AnketEmailSerializer(many=True, read_only=True)
    total_sum = serializers.DecimalField(max_digits=12, decimal_places=0)
    full_name = serializers.CharField()
    email = serializers.CharField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    social = ListCharField(fields=('user.facebook', 'user.vkontakte', 'user.odnoklassniki', 'user.skype'))
    region = serializers.CharField(source='user.region')
    district = serializers.CharField(source='user.district')
    address = serializers.CharField(source='user.address')
    born_date = serializers.CharField(source='user.born_date')
    repentance_date = serializers.CharField(source='user.repentance_date')
    spiritual_level = serializers.CharField(source='get_spiritual_level_display')
    ticket_status = ReadOnlyChoiceWithKeyField(choices=SummitAnket.TICKET_STATUSES, read_only=True)

    class Meta:
        model = SummitAnket
        fields = ('id', 'user_id', 'full_name', 'responsible', 'spiritual_level',
                  'divisions_title', 'department', 'hierarchy_title', 'phone_number', 'email', 'social',
                  'country', 'city', 'region', 'district', 'address', 'born_date', 'repentance_date',
                  'code', 'value', 'description',
                  'emails',
                  'visited',
                  'link',
                  'ticket_status',

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


class ChildrenLink(serializers.RelatedField):
    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            self.view_name = view_name
        assert self.view_name is not None, 'The `view_name` argument is required.'
        self.summit_id = kwargs.pop('summit_kwarg', 'summit_id')
        self.master_id = kwargs.pop('master_kwarg', 'master_id')

        super(ChildrenLink, self).__init__(**kwargs)

    def get_attribute(self, instance):
        summit_id = instance.summit_id
        master_id = instance.user_id
        has_children = instance.diff // 2 > 0

        return summit_id, master_id, has_children

    def to_representation(self, value):
        summit_id, master_id, has_children = value
        if has_children:
            return reverse(self.view_name, kwargs={self.summit_id: summit_id, self.master_id: master_id})
        return None


class SummitProfileTreeForAppSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    master_fio = serializers.CharField(source='responsible')
    user_id = serializers.IntegerField(source='user.user_ptr_id')
    phone_number = serializers.CharField(source='user.phone_number')
    extra_phone_numbers = serializers.ListField(source='user.extra_phone_numbers')
    children = ChildrenLink(view_name='summit-app-profile-list-master', queryset=SummitAnket.objects.all())

    class Meta:
        model = SummitAnket
        fields = (
            'id', 'user_id', 'master_id',
            'full_name', 'country', 'city', 'phone_number', 'extra_phone_numbers',
            'master_fio', 'hierarchy_id', 'children',
        )


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
        fields = ('first_name', 'last_name', 'middle_name', 'country', 'city', 'email', 'phone_number') \
            #  + ('region', 'district', 'address', 'image_source')


class SummitAnketForAppSerializer(serializers.ModelSerializer):
    user = UserForAppSerializer()
    ticket_id = serializers.CharField(source='code')
    visitor_id = serializers.IntegerField(source='id')

    class Meta:
        model = SummitAnket
        fields = ('visitor_id', 'user', 'ticket_id', 'reg_code')  # + ('value', 'is_member')


class SummitAnketLocationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.fullname')

    class Meta:
        model = SummitAnket
        fields = ('id', 'fullname')


class SummitVisitorLocationSerializer(serializers.ModelSerializer):
    # visitor = SummitAnketLocationSerializer()

    class Meta:
        model = SummitVisitorLocation
        fields = ('visitor', 'date_time', 'longitude', 'latitude')


class SummitEventTableSerializer(serializers.ModelSerializer):
    summit_id = serializers.IntegerField(source='summit.id')

    class Meta:
        model = SummitEventTable
        fields = ('summit_id', 'date', 'time', 'name_ru', 'author_ru', 'name_en',
                  'author_en', 'name_de', 'author_de')
