# -*- coding: utf-8
from models import Summit, SummitAnket, SummitType
from rest_framework import serializers
from account.models import CustomUser as User


class SummitAnketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SummitAnket
        fields = ('info', 'common', 'code', )


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
        fields = ('id', 'city', 'fullname', 'country', 'master_short_fullname')
