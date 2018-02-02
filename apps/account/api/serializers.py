# -*- coding: utf-8
from __future__ import unicode_literals

import binascii
import os
import traceback

from django.conf import settings
from django.contrib.auth import authenticate
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_framework.validators import UniqueTogetherValidator, qs_exists

from apps.account.models import CustomUser as User, CustomUser
from apps.location.api.serializers import CityTitleSerializer, CityReadSerializer
from common.fields import ReadOnlyChoiceField
from apps.group.models import Church, HomeGroup
from apps.hierarchy.models import Department, Hierarchy
from apps.partnership.models import Partnership
from apps.status.models import Division
from apps.summit.models import SummitAnket, Summit

BASE_USER_FIELDS = (
    'id',
    # 'username',
    'email', 'first_name', 'last_name', 'middle_name', 'search_name',
    'facebook', 'vkontakte', 'odnoklassniki', 'skype',
    'description', 'spiritual_level',

    'phone_number', 'extra_phone_numbers',
    'born_date', 'coming_date', 'repentance_date',

    'country', 'region', 'city', 'district', 'address', 'marker',
    'locality',
    # #################################################
    'image', 'image_source',

    'master', 'hierarchy',
    'partners',
    'departments', 'divisions',
    # read_only
    'fullname',
    'is_dead', 'is_stable',
)

PARTNER_USER_FIELDS = (
    'id',
    'fullname',
    'email', 'first_name', 'last_name', 'middle_name', 'search_name',
    'phone_number', 'born_date', 'repentance_date', 'spiritual_level',
    'master', 'hierarchy',
    'departments', 'divisions',
    'get_church',
    'country', 'region', 'city', 'district', 'address',
    'locality',
    # 'username',
    # read_only
    'is_dead', 'is_stable',
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
    master = MasterNameSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'city', 'country', 'full_name', 'can_add', 'master')


class ChurchNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Church
        fields = ('id', 'title',)


def exist_users_with_level_not_in_levels(users, levels):
    return users.exclude(hierarchy__level__in=levels).exists()


class PartnerUserSerializer(serializers.ModelSerializer):
    departments = DepartmentTitleSerializer(many=True, read_only=True)
    master = MasterNameSerializer(required=False, allow_null=True)
    hierarchy = HierarchyTitleSerializer()
    divisions = DivisionSerializer(many=True, read_only=True)
    spiritual_level = ReadOnlyChoiceField(choices=User.SPIRITUAL_LEVEL_CHOICES, read_only=True)
    get_church = ChurchNameSerializer(read_only=True)
    locality = CityTitleSerializer()

    class Meta:
        model = User
        fields = PARTNER_USER_FIELDS


class BaseUserSerializer(serializers.ModelSerializer):
    partners = PartnershipSerializer(many=True, read_only=True)
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

    @staticmethod
    def make_phone_number(phone_number):
        return '+' + ''.join([x for x in phone_number if x.isdigit()])

    def validate_phone_number(self, value):
        value = self.make_phone_number(value)
        if len(value) < 11:
            raise serializers.ValidationError(
                {'message': _('The length of the phone number must be at least 10 digits')})
        return value

    def validate_extra_phone_numbers(self, value):
        extra_phone_numbers = [self.make_phone_number(number) for number in value]
        for number in extra_phone_numbers:
            if len(number) < 11:
                raise serializers.ValidationError(
                    {'message': _('The length of the phone number must be at least 10 digits')})
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
        divisions = validated_data.pop('divisions', None)
        markers = validated_data.pop('marker', None)
        master = validated_data.get('master', None)
        move_to_master = validated_data.pop('move_to_master', None)

        if move_to_master is not None:
            disciples = user.disciples.all()
            to_master = User.objects.get(id=move_to_master)
            disciples.update(master=to_master)
            for d in disciples:
                d.move(to_master, pos='last-child')

        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()
        if master:
            user.move(master, pos='last-child')
        elif 'master' in validated_data and master is None:
            root = user.get_root()
            user.move(root, 'last-sibling')

        if departments is not None and isinstance(departments, (list, tuple)):
            user.departments.set(departments)

            if user.cchurch and user.cchurch.department not in user.departments.all():
                user.hhome_group = None
                user.cchurch = None
                user.save()
        if divisions is not None:
            user.divisions.set(divisions)
        if markers is not None:
            user.marker.set(markers)

        for profile in user.summit_profiles.all():
            profile.save()
        SummitAnket.objects.filter(
            summit__status=Summit.OPEN,
            user_id__in=user.disciples.values_list('pk', flat=True)).update(responsible=user.fullname)

        return user

    def validate_master(self, master):
        if master and master.is_descendant_of(self.instance):
            raise ValidationError({'master': _("Can't move user to a descendant.")})
        return master

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
    is_stable = serializers.BooleanField(default=True)

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
        master = validated_data.get('master')

        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            if master:
                instance = master.add_child(**validated_data)
            else:
                instance = CustomUser.add_root(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                    'Got a `TypeError` when calling `%s.objects.create()`. '
                    'This may be because you have a writable field on the '
                    'serializer class that is not a valid argument to '
                    '`%s.objects.create()`. You may need to make the field '
                    'read-only, or override the %s.create() method to handle '
                    'this correctly.\nOriginal exception was:\n %s' %
                    (
                        ModelClass.__name__,
                        ModelClass.__name__,
                        self.__class__.__name__,
                        tb
                    )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance


class UserSingleSerializer(BaseUserSerializer):
    departments = DepartmentTitleSerializer(many=True, read_only=True)
    master = MasterWithHierarchySerializer(required=False, allow_null=True)
    hierarchy = HierarchyTitleSerializer()
    divisions = DivisionSerializer(many=True, read_only=True)
    spiritual_level = ReadOnlyChoiceField(choices=User.SPIRITUAL_LEVEL_CHOICES, read_only=True)
    locality = CityReadSerializer()


class UserTableSerializer(UserSingleSerializer):
    master = MasterNameSerializer(required=False, allow_null=True)
    get_church = ChurchNameSerializer(read_only=True)
    locality = CityTitleSerializer()

    class Meta(UserSingleSerializer.Meta):
        fields = BASE_USER_FIELDS + ('get_church',)
        required_fields = ('id', 'link', 'extra_phone_numbers', 'description')

    def get_field_names(self, declared_fields, info):
        # fields = getattr(self.Meta, 'fields', None)
        # if self.context.get('request', None):
        #     user = self.context['request'].user
        #     if hasattr(user, 'table') and isinstance(user.table, Table):
        #         columns = user.table.columns.filter(
        #             columnType__category__title="Общая информация",
        #             active=True).order_by('number').values_list('columnType__title', flat=True)
        #     else:
        #         columns = list()
        #     if 'social' in columns:
        #         columns = list(columns) + ['facebook', 'vkontakte', 'odnoklassniki', 'skype', 'image', 'image_source']
        #     return list(self.Meta.required_fields) + [i for i in columns if i != 'social']
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


class RestAuthLoginSerializer(LoginSerializer):
    email = serializers.CharField(required=False, allow_blank=True)

    def _validate_user_id(self, user_id, password):
        user = None

        if user_id and password:
            user = authenticate(user_id=user_id, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email and email.isdigit():
                user = self._validate_user_id(email, password)
            elif email:
                try:
                    username = CustomUser.objects.get(email__iexact=email, can_login=True).get_username()
                except CustomUser.DoesNotExist:
                    if CustomUser.objects.filter(email__iexact=email).exists():
                        msg = _('Вы не имеете право для входа на сайт.')
                        raise ValidationError(msg)
                    msg = _('Пользователя с таким email не существует.')
                    raise ValidationError(msg)
                except CustomUser.MultipleObjectsReturned:
                    msg = _('Есть несколько пользователей с таким email.')
                    raise ValidationError(msg)

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs
