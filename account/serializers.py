# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser as User, AdditionalPhoneNumber
from hierarchy.models import Department, Hierarchy
from partnership.models import Partnership
from status.models import Division


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'fullname', 'image', 'image_source',
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
        fields = ('id', 'title')
        read_only_fields = ('title',)


class MasterNameSerializer(serializers.ModelSerializer):
    # hierarchy = HierarchyTitleSerializer()

    class Meta:
        model = User
        fields = ('id', 'fullname',
                  # 'hierarchy'
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
        fields = ('id', 'value', 'responsible')


class NewUserSerializer(serializers.ModelSerializer):
    additional_phones = AdditionalPhoneSerializer(many=True, read_only=True)

    partnership = PartnershipSerializer()

    class Meta:
        model = User
        fields = ('id',
                  'email', 'first_name', 'last_name', 'middle_name',
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
        required_fields = ('id', 'link',)

    def update(self, instance, validated_data):
        department = validated_data.pop('department') if validated_data.get('department') else None
        master = validated_data.pop('master') if validated_data.get('master') else None
        hierarchy = validated_data.pop('hierarchy') if validated_data.get('hierarchy') else None
        additional_phone = validated_data.pop('additional_phone') if validated_data.get('additional_phone') else None
        # coming_date = validated_data.pop('coming_date') if validated_data.get('coming_date') else None
        # repentance_date = validated_data.pop('repentance_date') if validated_data.get('repentance_date') else None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class UserTableSerializer(NewUserSerializer):
    department = DepartmentTitleSerializer()
    master = MasterNameSerializer(required=False, allow_null=True)
    hierarchy = HierarchyTitleSerializer()
    divisions = DivisionSerializer(many=True, read_only=True)

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
    class Meta:
        model = User
        fields = ('id', 'fullname')
