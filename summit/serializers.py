# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser as User
from account.serializers import NewUserSerializer
from .models import Summit, SummitAnket, SummitType, SummitAnketNote


class SummitAnketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SummitAnket
        fields = ('info', 'common', 'code',)


class NewSummitAnketSerializer(serializers.HyperlinkedModelSerializer):
    user = NewUserSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'user', 'code', 'value', 'description')


class SummitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'title', 'description')


class SummitTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SummitType
        fields = ('id', 'title', 'image')


class SummitUnregisterUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'fullname')


class SummitAnketNoteSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = SummitAnketNote
        fields = ('summit_anket', 'text', 'owner', 'date_created')
        read_only_fields = ('owner', 'date_created', 'id')
        extra_kwargs = {'summit_anket': {'write_only': True}}


class SummitAnketWithNotesSerializer(serializers.ModelSerializer):
    notes = SummitAnketNoteSerializer(many=True, read_only=True)

    class Meta:
        model = SummitAnket
        fields = ('info', 'common', 'code', 'notes')
