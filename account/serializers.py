# -*- coding: utf-8
from __future__ import unicode_literals

import binascii
import os

from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator, qs_exists

from account.models import CustomUser as User
from common.fields import ReadOnlyChoiceField
from group.models import Church, HomeGroup
from hierarchy.models import Department, Hierarchy
from navigation.models import Table
from partnership.models import Partnership
from status.models import Division

BASE_USER_FIELDS = (
    'id',
    # 'username',
    'email', 'first_name', 'last_name', 'middle_name', 'search_name',
    'facebook', 'vkontakte', 'odnoklassniki', 'skype',
    'description', 'spiritual_level',

    'phone_number', 'extra_phone_numbers',
    'born_date', 'coming_date', 'repentance_date',

    'country', 'region', 'city', 'district', 'address',
    # #################################################
    'image', 'image_source',

    'master', 'hierarchy',
    'partnership',
    'departments', 'divisions',
    # read_only
    'fullname',
)


class HierarchyError(Exception):
    pass


def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


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


class PartnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = ('value', 'responsible', 'date', 'user', 'currency', 'is_active')


class AddExistUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    can_add = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'city', 'country', 'full_name', 'can_add')


def exist_users_with_level_not_in_levels(users, levels):
    return users.exclude(hierarchy__level__in=levels).exists()


class BaseUserSerializer(serializers.ModelSerializer):
    partnership = PartnershipSerializer(required=False)
    move_to_master = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = BASE_USER_FIELDS
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},

            'hierarchy': {'required': True},
            'departments': {'required': True},
            # 'master': {'required': True},

            'divisions': {'required': False},
        }

    def validate_hierarchy(self, value):
        reduce_level = lambda: self.instance and self.instance.hierarchy and value.level < self.instance.hierarchy.level

        def has_disciples():
            return exist_users_with_level_not_in_levels(
                self.instance.disciples, settings.CHANGE_HIERARCHY_LEVELS[value.level])

        has_move_disciples = lambda: 'move_to_master' in self.initial_data.keys()
        if reduce_level() and has_disciples() and not has_move_disciples():
            raise HierarchyError()
        return value

    def validate(self, attrs):
        if 'master' in attrs.keys():
            if 'hierarchy' in attrs.keys():
                if attrs['hierarchy'].level < 70 and not attrs['master']:
                    raise ValidationError({'master': _('Master is required field.')})
            elif self.instance.hierarchy.level < 70 and not attrs['master']:
                raise ValidationError({'master': _('Master is required field.')})
        return attrs


class UserSerializer(BaseUserSerializer):
    pass


class UserUpdateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = BASE_USER_FIELDS + ('move_to_master',)

    def update(self, user, validated_data):
        departments = validated_data.pop('departments', None)
        move_to_master = validated_data.pop('move_to_master', None)

        if move_to_master is not None:
            disciples = user.disciples.all()
            master = User.objects.get(id=move_to_master)
            disciples.update(master=master)

        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()

        if departments is not None and isinstance(departments, (list, tuple)):
            user.departments.set(departments)

        return user

    def validate_move_to_master(self, value):
        if not User.objects.filter(id=value).exists():
            raise ValidationError({'detail': _('User with id = %s does not exist.' % value)})
        return value


class UserForMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name')


class UniqueFIOTelWithIdsValidator(UniqueTogetherValidator):
    message = _('Пользователь с такими ФИО и телефоном уже существует.')

    def __call__(self, attrs):
        self.enforce_required_fields(attrs)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset)
        queryset = self.exclude_current_instance(attrs, queryset)

        # Ignore validation if any field is None
        checked_values = [value for field, value in attrs.items() if field in self.fields]
        if None not in checked_values and qs_exists(queryset):
            ids = list(queryset.values_list('id', flat=True))
            data = dict(zip(self.fields, checked_values))
            raise ValidationError({'detail': self.message,
                                   'data': data,
                                   'ids': ids,
                                   'users': [reverse('account:detail', args=(pk,)) for pk in ids]
                                   }, )


class UserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        validators = (UniqueFIOTelWithIdsValidator(
            queryset=User.objects.all(),
            fields=['phone_number', 'first_name', 'last_name', 'middle_name']
        ),)

    def create(self, validated_data):
        username = generate_key()[:20]
        # while User.objects.filter(username=username).exists():
        #     username = generate_key()

        validated_data['username'] = username

        return super(BaseUserSerializer, self).create(validated_data)


class UserSingleSerializer(BaseUserSerializer):
    departments = DepartmentTitleSerializer(many=True, read_only=True)
    master = MasterWithHierarchySerializer(required=False, allow_null=True)
    hierarchy = HierarchyTitleSerializer()
    divisions = DivisionSerializer(many=True, read_only=True)
    spiritual_level = ReadOnlyChoiceField(choices=User.SPIRITUAL_LEVEL_CHOICES, read_only=True)


class UserTableSerializer(UserSingleSerializer):
    master = MasterNameSerializer(required=False, allow_null=True)

    class Meta(UserSingleSerializer.Meta):
        required_fields = ('id', 'link', 'extra_phone_numbers', 'description')

    def get_field_names(self, declared_fields, info):
        # fields = getattr(self.Meta, 'fields', None)
        if self.context.get('request', None):
            user = self.context['request'].user
            if hasattr(user, 'table') and isinstance(user.table, Table):
                columns = user.table.columns.filter(
                    columnType__category__title="Общая информация",
                    active=True).order_by('number').values_list('columnType__title', flat=True)
            else:
                columns = list()
            if 'social' in columns:
                columns = list(columns) + ['facebook', 'vkontakte', 'odnoklassniki', 'skype', 'image', 'image_source']
            return list(self.Meta.required_fields) + [i for i in columns if i != 'social']
        return getattr(self.Meta, 'fields', None)


class UserShortSerializer(serializers.HyperlinkedModelSerializer):
    hierarchy = HierarchyTitleSerializer()

    class Meta:
        model = User
        fields = ('id', 'fullname', 'hierarchy')


class UserForSelectSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='full_name')

    class Meta:
        model = User
        fields = ('id', 'title')


class ExistUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'fullname', 'phone_number', 'email', 'link')


class DashboardSerializer(serializers.ModelSerializer):
    fathers_count = serializers.IntegerField()
    juniors_count = serializers.IntegerField()
    babies_count = serializers.IntegerField()
    total_peoples = serializers.IntegerField()
    leaders_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('total_peoples', 'fathers_count', 'juniors_count', 'babies_count', 'leaders_count')
        read_only_fields = ['__all__']


class ChurchIdSerializer(serializers.ModelSerializer):
    church_id = serializers.ModelField(model_field='pk')

    class Meta:
        model = Church
        fields = ('church_id',)


class HomeGroupIdSerializer(serializers.ModelSerializer):
    home_group_id = serializers.ModelField(model_field='pk')

    class Meta:
        model = HomeGroup
        fields = ('home_group_id',)


class DuplicatesAvoidedSerializer(serializers.ModelSerializer):
    master = MasterNameSerializer(read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'last_name', 'first_name', 'middle_name', 'phone_number',
                  'master', 'city', 'link')
