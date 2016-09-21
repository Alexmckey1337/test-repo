# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    theme = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = ('url', 'id', 'theme', 'fullname', 'uid', 'description', 'date', 'common', 'system',)
