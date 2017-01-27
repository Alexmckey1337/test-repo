# -*- coding: utf-8
from rest_framework import serializers
from .models import Church, HomeGroup
from account.models import CustomUser
from account.serializers import DepartmentTitleSerializer
from django.utils.translation import ugettext as _


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


class HomeGroupLeaderRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': 'Данный пользователь "{pk_value}" - не может быть назначен лидером Домашней Группы.',
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.'),
    }


class HomeGroupSerializer(serializers.ModelSerializer):
    leader = HomeGroupLeaderRelatedField(queryset=CustomUser.objects.filter(hierarchy__level__gt=0))

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


class ChurchPastorRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': 'Данный пользователь "{pk_value}" - не может быть назначен пастором Церкви.',
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.'),
    }


class ChurchSerializer(serializers.ModelSerializer):
    count_groups = serializers.IntegerField(read_only=True)
    count_users = serializers.IntegerField(read_only=True)
    link = serializers.CharField(read_only=True)
    pastor = ChurchPastorRelatedField(queryset=CustomUser.objects.filter(hierarchy__level__gt=1))

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
