# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from status.models import Status, Division


class StatusSerializer(serializers.HyperlinkedModelSerializer):
    # day = serializers.IntegerField(read_only=True)

    class Meta:
        model = Status
        fields = ('url', 'id', 'title',)


class DivisionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Division
        fields = ('url', 'id', 'title',)
