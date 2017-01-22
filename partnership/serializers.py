# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser
from account.serializers import UserTableSerializer
from .models import Partnership, Deal


class PartnershipForEditSerializer(serializers.ModelSerializer):
    responsible_id = serializers.PrimaryKeyRelatedField(source='responsible', read_only=True)

    class Meta:
        model = Partnership
        fields = ('date', 'responsible_id', 'value')


class PartnershipSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format=None, input_formats=None)
    responsible = serializers.StringRelatedField()
    user = UserTableSerializer()

    class Meta:
        model = Partnership
        fields = ('id', 'user', 'responsible', 'value', 'is_responsible', 'date',
                  'fullname', 'need_text', 'level', 'currency', 'is_active',
                  )


class DealSerializer(serializers.HyperlinkedModelSerializer):
    date = serializers.DateField(format=None, input_formats=None, read_only=True)
    date_created = serializers.DateField(input_formats=None)
    partnership = serializers.PrimaryKeyRelatedField(queryset=Partnership.objects.all())
    full_name = serializers.CharField(read_only=True)
    responsible_name = serializers.CharField(read_only=True)
    total_sum = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)

    class Meta:
        model = Deal
        fields = ('url', 'id', 'partnership', 'date', 'date_created',
                  'value', 'done', 'expired', 'description',
                  'full_name', 'responsible_name',
                  'total_sum'
                  )


class PartnershipUnregisterUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname')
