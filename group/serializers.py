# -*- coding: utf-8
from django.utils.translation import ugettext as _
from rest_framework import serializers

from account.models import CustomUser
from account.serializers import DepartmentTitleSerializer
from common.fields import ReadOnlyChoiceField
from .models import Church, HomeGroup

BASE_GROUP_USER_FIELDS = ('fullname', 'phone_number', 'repentance_date', 'spiritual_level',
                          'born_date')


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname',)


class ChurchNameSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='get_title', read_only=True)

    class Meta:
        model = Church
        fields = ('id', 'title',)


class HomeGroupNameSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='get_title', read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'title')


class HomeGroupLeaderRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Данный пользователь "{pk_value}" - '
                            'не может быть назначен лидером Домашней Группы.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.')
    }


class HomeGroupSerializer(serializers.ModelSerializer):
    leader = HomeGroupLeaderRelatedField(queryset=CustomUser.objects.filter(
        hierarchy__level__gt=0))
    department = serializers.CharField(source='church.department.id', read_only=True)
    count_users = serializers.IntegerField(read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'link', 'opening_date', 'title', 'city', 'department',
                  'get_title', 'church', 'leader', 'address', 'phone_number',
                  'website', 'count_users')


class HomeGroupListSerializer(HomeGroupSerializer):
    church = ChurchNameSerializer()
    leader = UserNameSerializer()


class GroupUserSerializer(serializers.ModelSerializer):
    spiritual_level = ReadOnlyChoiceField(
        choices=CustomUser.SPIRITUAL_LEVEL_CHOICES, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'link') + BASE_GROUP_USER_FIELDS


class HomeGroupDetailSerializer(serializers.ModelSerializer):
    users = GroupUserSerializer(many=True, read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'users')


class ChurchPastorRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Данный пользователь "{pk_value}" - '
                            'не может быть назначен пастором Церкви.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.')
    }


class ChurchSerializer(serializers.ModelSerializer):
    count_groups = serializers.IntegerField(read_only=True)
    count_users = serializers.IntegerField(read_only=True)
    link = serializers.CharField(read_only=True)
    pastor = ChurchPastorRelatedField(queryset=CustomUser.objects.filter(
        hierarchy__level__gte=2))

    class Meta:
        model = Church
        fields = ('id', 'opening_date', 'is_open', 'link', 'title', 'get_title',
                  'department', 'pastor', 'country', 'city', 'address', 'website',
                  'phone_number', 'count_groups', 'count_users')


class ChurchListSerializer(ChurchSerializer):
    department = DepartmentTitleSerializer()
    pastor = UserNameSerializer()


class ChurchWithoutPaginationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Church
        fields = ('id', 'get_title')


class ChurchStatsSerializer(serializers.ModelSerializer):
    church_users = serializers.IntegerField()
    church_all_users = serializers.IntegerField()
    parishioners_count = serializers.IntegerField()
    leaders_count = serializers.IntegerField()
    home_groups_count = serializers.IntegerField()
    fathers_count = serializers.IntegerField()
    juniors_count = serializers.IntegerField()
    babies_count = serializers.IntegerField()
    partners_count = serializers.IntegerField()

    class Meta:
        model = Church
        fields = ('church_users', 'church_all_users', 'parishioners_count', 'leaders_count',
                  'leaders_count', 'home_groups_count', 'fathers_count', 'juniors_count',
                  'babies_count', 'partners_count')


class HomeGroupStatsSerializer(serializers.ModelSerializer):
    users_count = serializers.IntegerField()
    fathers_count = serializers.IntegerField()
    juniors_count = serializers.IntegerField()
    babies_count = serializers.IntegerField()
    partners_count = serializers.IntegerField()

    class Meta:
        model = HomeGroup
        fields = ('users_count', 'fathers_count', 'juniors_count', 'babies_count',
                  'partners_count')


class AllChurchesListSerializer(serializers.ModelSerializer):
    get_title = serializers.CharField(read_only=True)

    class Meta:
        model = Church
        fields = ('id', 'get_title')


class AllHomeGroupsListSerializer(serializers.ModelSerializer):
    get_title = serializers.CharField(read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'get_title')

from django.db.models import Count
