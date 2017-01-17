# -*- coding: utf-8
from rest_framework import serializers
from .models import Church, HomeGroup
from account.models import CustomUser
from account.serializers import DepartmentTitleSerializer


class LeaderNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname')


class PastorNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname')


class HomeGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomeGroup
        fields = ('id', 'opening_date', 'title', 'city', 'church',
                  'leader', 'address', 'phone_number', 'website',)


class GroupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname', 'phone_number', 'repentance_date',
                  'spiritual_level', 'born_date',)


class HomeGroupDetailSerializer(serializers.ModelSerializer):
    users = GroupUserSerializer(many=True, read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'users')


class ChurchSerializer(serializers.ModelSerializer):
    count_groups = serializers.IntegerField(read_only=True)
    count_users = serializers.IntegerField(read_only=True)
    link = serializers.CharField(read_only=True)
    get_title = serializers.CharField(read_only=True)
    display_title = serializers.CharField(read_only=True)

    class Meta:
        model = Church
        fields = ('id', 'link', 'opening_date', 'is_open', 'title', 'get_title',
                  'display_title', 'department', 'city', 'pastor', 'address',
                  'phone_number', 'website', 'count_groups', 'count_users',)


class ChurchListSerializer(ChurchSerializer):
    department = DepartmentTitleSerializer()
    pastor = PastorNameSerializer()

    def get_field_names(self, declared_fields, info):
        return getattr(self.Meta, 'fields', None)


class ChurchDetailSerializer(serializers.ModelSerializer):
    home_group = HomeGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Church
        fields = ('id', 'home_group',)
