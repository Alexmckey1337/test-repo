# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser as User
from .models import LastCall, Synopsis


class LastCallSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LastCall
        fields = ('url', 'date', 'id', 'last_responce', 'user_info', 'attrs',)


class UserLittleSerializer(serializers.HyperlinkedModelSerializer):
    # fields = serializers.OrderedDict()
    # master_leaderships = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ('id', 'city', 'phone_number', 'department_title', 'email',
                  'fullname', 'last_week_calls', 'attrs',)


class SynopsisSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Synopsis
        fields = ('fields',
                  'interviewer',
                  'id',
                  'date',
                  'url',)
