# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from account.models import CustomUser as User, Consultant
from hierarchy.models import Department, Hierarchy
from status.models import Division


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'fullname', 'image', 'image_source', 'consultant',
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
    class Meta:
        model = User
        fields = ('id', 'fullname')


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ('id', 'title')


class ConsultantForSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = ('id', 'fullname')


class NewUserSerializer(serializers.ModelSerializer):
    department = DepartmentTitleSerializer()
    master = MasterNameSerializer(required=False, allow_null=True)
    hierarchy = HierarchyTitleSerializer()
    divisions = DivisionSerializer(many=True, read_only=True)
    consultant = ConsultantForSelectSerializer()

    class Meta:
        model = User
        fields = ('id', 'email', 'fullname', 'department', 'master', 'phone_number', 'hierarchy', 'consultant',
                  'divisions', 'country', 'born_date', 'region', 'city', 'district', 'address', 'facebook')
        required_fields = ('id', 'link')

    def get_field_names(self, declared_fields, info):
        # fields = getattr(self.Meta, 'fields', None)
        if self.context.get('request', None):
            user = self.context['request'].user
            columns = user.table.columns.filter(
                columnType__category__title="Общая информация",
                active=True).order_by('number').values_list('columnType__title', flat=True)
            return list(self.Meta.required_fields) + [i for i in columns if i != 'social']
        return getattr(self.Meta, 'fields', None)

    def update(self, instance, validated_data):
        department = validated_data.pop('department')
        master = validated_data.pop('master')
        hierarchy = validated_data.pop('hierarchy')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class UserShortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'fullname')
