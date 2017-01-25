# -*- coding: utf-8
from rest_framework import serializers
from .models import Church, HomeGroup
from account.models import CustomUser
from account.serializers import DepartmentTitleSerializer


class LeaderNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname',)


class PastorNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname',)


class ChurchNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Church
        fields = ('id', 'get_title',)


class HomeGroupSerializer(serializers.ModelSerializer):
    leader = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(hierarchy__level__gt=0))

    class Meta:
        model = HomeGroup
        fields = ('id', 'opening_date', 'title', 'get_title', 'city',
                  'church', 'leader', 'address', 'phone_number', 'website',)


class HomeGroupListSerializer(HomeGroupSerializer):
    church = ChurchNameSerializer()
    leader = LeaderNameSerializer()

    def get_field_names(self, declared_fields, info):
        return getattr(self.Meta, 'fields', None)


class HomeGroupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname', 'phone_number', 'repentance_date', 'spiritual_level',
                  'born_date',)


class HomeGroupDetailSerializer(serializers.ModelSerializer):
    users = HomeGroupUserSerializer(many=True, read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'users')


class ChurchSerializer(serializers.ModelSerializer):
    count_groups = serializers.IntegerField(read_only=True)
    count_users = serializers.IntegerField(read_only=True)
    link = serializers.CharField(read_only=True)
    pastor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(hierarchy__level__gt=1))

    class Meta:
        model = Church
        fields = ('id', 'opening_date', 'is_open', 'link', 'title', 'get_title',
                  'department', 'pastor', 'country', 'city', 'address', 'phone_number',
                  'website', 'count_groups', 'count_users',)


class ChurchListSerializer(ChurchSerializer):
    department = DepartmentTitleSerializer()
    pastor = PastorNameSerializer()

    def get_field_names(self, declared_fields, info):
        return getattr(self.Meta, 'fields', None)


class ChurchDetailSerializer(serializers.ModelSerializer):
    home_group = HomeGroupListSerializer(many=True)

    class Meta:
        model = Church
        fields = ('id', 'home_group',)
