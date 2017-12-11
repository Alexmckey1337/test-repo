# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from apps.account.api.serializers import MasterNameSerializer
from apps.account.models import CustomUser


class NotificationBaseSerializer(serializers.ModelSerializer):
    master = MasterNameSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'fullname', 'link', 'phone_number', 'master')


class BirthdayNotificationSerializer(NotificationBaseSerializer):
    class Meta(NotificationBaseSerializer.Meta):
        fields = NotificationBaseSerializer.Meta.fields + ('born_date',)


class RepentanceNotificationSerializer(NotificationBaseSerializer):
    class Meta(NotificationBaseSerializer.Meta):
        fields = NotificationBaseSerializer.Meta.fields + ('repentance_date',)
