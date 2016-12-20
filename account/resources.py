# -*- coding: utf-8
from __future__ import unicode_literals

from import_export import fields

from account.models import CustomUser as User
from common.resources import CustomFieldsModelResource


class UserResource(CustomFieldsModelResource):
    """For excel import/export"""
    master_name = fields.Field()
    department_title = fields.Field()
    hierarchy_title = fields.Field()

    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name', 'middle_name',
                  'email', 'phone_number', 'skype', 'country', 'city', 'address',
                  'department_title', 'hierarchy_title', 'master_name',
                  'born_date', 'facebook', 'vkontakte', 'description',)

    def dehydrate_master_name(self, user):
        return '%s %s %s' % (user.first_name, user.last_name, user.middle_name)

    def dehydrate_department_title(self, user):
        return user.department.title if user.department else ''

    def dehydrate_hierarchy_title(self, user):
        return user.hierarchy.title if user.hierarchy else ''


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


def get_disciples(user):
    disciples = user.disciples.all()
    queryset = disciples
    for disciple in disciples.all():
        if disciple.has_disciples:
            queryset = queryset | get_disciples(disciple)
    return queryset
