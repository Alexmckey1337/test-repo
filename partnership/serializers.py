# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser
from account.serializers import NewUserSerializer
from .models import Partnership, Deal


class PartnershipSerializer(serializers.HyperlinkedModelSerializer):
    date = serializers.DateField(format=None, input_formats=None)
    responsible = serializers.StringRelatedField()

    class Meta:
        model = Partnership
        fields = ('url', 'id', 'user', 'fullname', 'responsible', 'value', 'date', 'need_text',
                  'is_responsible', 'deals', 'deals_count', 'done_deals_count', 'undone_deals_count',
                  'expired_deals_count', 'result_value', 'fields', 'deal_fields', 'common',)


class NewPartnershipSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format=None, input_formats=None)
    responsible = serializers.StringRelatedField()
    user = NewUserSerializer()
    # result_value = serializers.IntegerField()
    count = serializers.IntegerField()

    class Meta:
        model = Partnership
        fields = ('id', 'user', 'responsible', 'value', 'is_responsible', 'date',
                  'fullname',
                  'result_value',
                  'count'
                  )

    def get_field_names(self, declared_fields, info):
        fields = getattr(self.Meta, 'fields', None)
        return fields

    def update(self, instance, validated_data):
        user = validated_data.pop('user')
        user_serializer = NewUserSerializer(CustomUser.objects.get(id=self.data['user']['id']), user,
                                            partial=self.partial)
        user_serializer.is_valid(raise_exception=True)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        user_serializer.save()

        return instance


class DealSerializer(serializers.HyperlinkedModelSerializer):
    date = serializers.DateField(format=None, input_formats=None)

    class Meta:
        model = Deal
        fields = ('url', 'id', 'partnership', 'date', 'date_created',
                  'value', 'done', 'expired', 'description', 'fields',)


class PartnershipUnregisterUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname')
