# -*- coding: utf-8
from __future__ import unicode_literals

from import_export import fields
from import_export.resources import ModelDeclarativeMetaclass

from apps.account.models import CustomUser as User
from common.resources import CustomFieldsModelResource

USER_MAIN_RESOURCE_FIELDS = (
    'last_name', 'first_name', 'middle_name', 'region',
    'email', 'phone_number', 'skype', 'country', 'city', 'address',
    'born_date', 'facebook', 'vkontakte', 'description',
    'repentance_date', 'district')

USER_RESOURCE_FIELDS = USER_MAIN_RESOURCE_FIELDS + (
    'departments', 'hierarchy', 'master', 'spiritual_level', 'divisions', 'fullname')


class UserMetaclass(ModelDeclarativeMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = super(UserMetaclass,
                          mcs).__new__(mcs, name, bases, attrs)

        def create_dehydrate_method(f):
            def dehydrate_method(self, obj):
                user_field = self.get_user_field(obj)
                return getattr(user_field, f)

            return dehydrate_method

        for f in USER_MAIN_RESOURCE_FIELDS:
            setattr(new_class, 'dehydrate_{}'.format(f), create_dehydrate_method(f))
        return new_class


class UserResource(CustomFieldsModelResource):
    """For excel import/export"""
    divisions = fields.Field()
    fullname = fields.Field()
    get_church = fields.Field()
    home_group = fields.Field()

    user_field_name = None

    class Meta:
        model = User
        fields = USER_RESOURCE_FIELDS + ('cchurch', 'hhome_group')

    def get_user_field(self, user):
        if self.user_field_name:
            return getattr(user, self.user_field_name)
        return user

    def dehydrate_master(self, user):
        user_field = self.get_user_field(user)
        if not user_field.master:
            return ''
        return '%s %s %s' % (user_field.master.last_name, user_field.master.first_name, user_field.master.middle_name)

    def dehydrate_get_church(self, user):
        user_field = self.get_user_field(user)
        if not user_field.cchurch:
            if not user_field.hhome_group:
                return ''
            return user_field.hhome_group.church
        return user_field.cchurch

    def dehydrate_home_group(self, user):
        user_field = self.get_user_field(user)
        if not user_field.hhome_group:
            return ''
        return user_field.hhome_group

    def dehydrate_departments(self, user):
        user_field = self.get_user_field(user)
        return ', '.join(user_field.departments.values_list('title', flat=True))

    def dehydrate_hierarchy(self, user):
        user_field = self.get_user_field(user)
        return user_field.hierarchy.title if user_field.hierarchy else ''

    def dehydrate_spiritual_level(self, user):
        user_field = self.get_user_field(user)
        return user_field.get_spiritual_level_display()

    def dehydrate_divisions(self, user):
        user_field = self.get_user_field(user)
        return ', '.join(user_field.divisions.values_list('title', flat=True))

    def dehydrate_fullname(self, user):
        user_field = self.get_user_field(user)
        return user_field.fullname


def clean_password(data):
    password1 = data['password1']
    password2 = data['password2']
    if password1 and password2:
        if password1 == password2:
            return password2
        else:
            return False
    else:
        return False
