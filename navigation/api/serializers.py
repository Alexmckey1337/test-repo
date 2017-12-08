# -*- coding: utf-8
from __future__ import unicode_literals

import json

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from navigation.models import Navigation, ColumnType, Table, Column
from navigation.table_columns import TABLES
from notification.backend import RedisBackend


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


class ColumnListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        pass

    def get_attribute(self, instance):
        columns = super().get_attribute(instance)
        return json.loads(columns)

    def to_representation(self, data):
        columns = super().to_representation(data)
        return {
            col['name']: {
                'number': col['number'],
                'active': col['active']
            }
            for col in columns
        }


class RedisUpdateColumnSerializer(serializers.Serializer):
    name = serializers.CharField()
    number = serializers.IntegerField(min_value=1)
    active = serializers.BooleanField()

    class Meta:
        fields = ('name', 'number', 'active')
        list_serializer_class = ColumnListSerializer

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class RedisTableSerializer(serializers.Serializer):
    columns = RedisUpdateColumnSerializer(many=True, allow_null=False, allow_empty=False)
    name = serializers.CharField()

    class Meta:
        fields = ('columns', 'name')

    def create(self, validated_data):
        r = RedisBackend()
        data = json.dumps(validated_data.get('columns'))
        r.set('table:{}:{}'.format(validated_data.get('name'), validated_data.get('user_id')), data)
        return validated_data

    def validate_name(self, name):
        if name not in TABLES.keys():
            raise ValidationError(_('Table does not exist.'))
        return name

    def validate_columns(self, columns):
        if len(set(c['name'] for c in columns)) != len(list(c['name'] for c in columns)):
            raise ValidationError(_('Name of columns must be unique.'))
        return columns

    def to_representation(self, instance):
        r = RedisBackend()
        name, user_id = instance['name'], instance['user_id']
        columns = r.get('table:{}:{}'.format(name, user_id))
        if not columns:
            return {'name': name, columns: {}}
        instance = {'name': name, 'columns': columns}
        return super().to_representation(instance)
