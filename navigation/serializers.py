from models import Navigation, ColumnType, Table, Column
from rest_framework import serializers


class NavigationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Navigation
        fields = ('title', 'url', )


class TableSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Table
        fields = ('id', 'user', 'url', )


class ColumnTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ColumnType
        fields = ('id', 'title', 'url',)


class ColumnSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Column
        fields = ('id', 'url', 'table', 'columnType', 'number', 'active', )
