# -*- coding: utf-8
from __future__ import unicode_literals

import binascii
import os

from rest_framework import serializers

from account.models import CustomUser as User, AdditionalPhoneNumber
from hierarchy.models import Department, Hierarchy
from partnership.models import Partnership
from status.models import Division


def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'fullname', 'image', 'image_source', 'search_name',
                  'hierarchy_name', 'has_disciples', 'hierarchy_order', 'column_table',
                  'fields', 'division_fields', 'hierarchy_chain', 'partnerships_info')


class DepartmentTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'title')
        read_only_fields = ('title',)


class HierarchyTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = ('id', 'title', 'level')
        read_only_fields = ('title',)


class MasterNameSerializer(serializers.ModelSerializer):
    # hierarchy = HierarchyTitleSerializer()

    class Meta:
        model = User
        fields = ('id', 'fullname',
                  # 'hierarchy'
                  )


class MasterWithHierarchySerializer(serializers.ModelSerializer):
    hierarchy = HierarchyTitleSerializer()

    class Meta:
        model = User
        fields = ('id', 'fullname',
                  'hierarchy'
                  )


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ('id', 'title')


class AdditionalPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalPhoneNumber
        fields = ('id', 'number')


class PartnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = ('value', 'responsible', 'date', 'user')


class NewUserSerializer(serializers.ModelSerializer):
    additional_phones = AdditionalPhoneSerializer(many=True, read_only=True)

    partnership = PartnershipSerializer(required=False)

    class Meta:
        model = User
        fields = ('id',
                  # 'username',
                  'email', 'first_name', 'last_name', 'middle_name', 'search_name',
                  'facebook', 'vkontakte', 'odnoklassniki', 'skype',

                  'phone_number',
                  'additional_phones',
                  'born_date',
                  'coming_date', 'repentance_date',

                  'country', 'region', 'city', 'district', 'address',
                  # #################################################
                  'image', 'image_source',

                  'department', 'master', 'hierarchy',
                  'divisions',
                  'partnership',
                  # read_only
                  'fullname',
                  )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},

            'hierarchy': {'required': True},
            'department': {'required': True},
            'master': {'required': True},

            'divisions': {'required': False},
        }

    def update(self, instance, validated_data):
        # department = validated_data.pop('department') if validated_data.get('department') else None
        # master = validated_data.pop('master') if validated_data.get('master') else None
        # hierarchy = validated_data.pop('hierarchy') if validated_data.get('hierarchy') else None
        # coming_date = validated_data.pop('coming_date') if validated_data.get('coming_date') else None
        # repentance_date = validated_data.pop('repentance_date') if validated_data.get('repentance_date') else None
        validated_data.pop('additional_phone') if validated_data.get('additional_phone') else None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def create(self, validated_data):
        validated_data.pop('additional_phone') if validated_data.get('additional_phone') else None

        username = generate_key()
        # while User.objects.filter(username=username).exists():
        #     username = generate_key()

        validated_data['username'] = username

        return super(NewUserSerializer, self).create(validated_data)


class UserSingleSerializer(NewUserSerializer):
    department = DepartmentTitleSerializer()
    master = MasterWithHierarchySerializer(required=False, allow_null=True)
    hierarchy = HierarchyTitleSerializer()
    divisions = DivisionSerializer(many=True, read_only=True)


class UserTableSerializer(UserSingleSerializer):
    master = MasterNameSerializer(required=False, allow_null=True)

    class Meta(UserSingleSerializer.Meta):
        required_fields = ('id', 'link')

    def get_field_names(self, declared_fields, info):
        # fields = getattr(self.Meta, 'fields', None)
        if self.context.get('request', None):
            user = self.context['request'].user
            columns = user.table.columns.filter(
                columnType__category__title="Общая информация",
                active=True).order_by('number').values_list('columnType__title', flat=True)
            if 'social' in columns:
                columns = list(columns) + ['facebook', 'vkontakte', 'odnoklassniki', 'skype', 'image', 'image_source']
            return list(self.Meta.required_fields) + [i for i in columns if i != 'social']
        return getattr(self.Meta, 'fields', None)


class UserShortSerializer(serializers.HyperlinkedModelSerializer):
    hierarchy = HierarchyTitleSerializer()

    class Meta:
        model = User
        fields = ('id', 'fullname', 'hierarchy')
