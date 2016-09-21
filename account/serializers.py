# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser as User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'fullname', 'image', 'image_source',
                  'hierarchy_name', 'has_disciples', 'hierarchy_order', 'column_table',
                  'fields', 'division_fields', 'hierarchy_chain', 'partnerships_info')


class UserShortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'fullname')
