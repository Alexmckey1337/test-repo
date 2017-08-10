# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers
from account.models import CustomUser


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'link', 'first_name', 'middle_name', 'last_name')
