# -*- coding: utf-8
from __future__ import unicode_literals

from import_export import fields
from import_export.resources import ModelDeclarativeMetaclass

from account.models import CustomUser as User
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

    user_field_name = None

    class Meta:
        model = User
        fields = USER_RESOURCE_FIELDS

    def get_user_field(self, user):
        if self.user_field_name:
            return getattr(user, self.user_field_name)
        return user

    def dehydrate_master(self, user):
        user_field = self.get_user_field(user)
        if not user_field.master:
            return ''
        return '%s %s %s' % (user_field.master.last_name, user_field.master.first_name, user_field.master.middle_name)

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


def clean_old_password(user, data):
    if data["old_password"]:
        old_password = data["old_password"]
        if user and user.check_password(old_password):
            return old_password
        else:
            return False
    else:
        return False


def setHierarchyOrder(user, b):
    if user.master and user.master.hierarchy_order:

        master_salt = user.hierarchy_order
    else:
        exponent = (user.hierarchy.level - 1) * 2
        salt = pow(10, exponent)
        user.hierarchy_order = b * salt
        user.save()
        master_salt = user.hierarchy_order
    users = user.disciples.order_by('last_name').all()
    i = 1
    print("%s : %d" % (user.last_name, user.hierarchy_order))
    for user in users.all():
        exponent = (user.hierarchy.level - 1) * 2
        salt = pow(10, exponent)
        user.hierarchy_order = master_salt + (i * salt)
        user.save()
        print("%s : %d" % (user.last_name, user.hierarchy_order))
        i += 1


def manage(level):
    if level >= 2:
        masters = User.objects.filter(hierarchy__level=level).all()
        b = 1
        for master in masters.all():
            setHierarchyOrder(master, b)
            b += 1
    else:
        return "Низя"
    return "Оки"
