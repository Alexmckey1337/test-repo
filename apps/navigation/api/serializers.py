# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from apps.navigation.models import Navigation, ColumnType, Table, Column


class NavigationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Navigation
        fields = ('title', 'url',)


class TableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Table
        fields = ('id', 'user', 'url',)


class ColumnTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ColumnType
        fields = ('id', 'title', 'url',)


class ColumnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Column
        fields = ('id', 'url', 'table', 'columnType', 'number', 'active',)


class UpdateColumnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Column
        fields = ('id', 'number', 'active',)
