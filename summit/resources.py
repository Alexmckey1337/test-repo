# -*- coding: utf-8
from __future__ import unicode_literals

from shutil import copyfile

from django.conf import settings
from django.utils import six

from account.resources import UserResource, USER_RESOURCE_FIELDS, UserMetaclass
from hierarchy.models import Department
from .models import SummitAnket


class SummitAnketResource(six.with_metaclass(UserMetaclass, UserResource)):
    """For excel import/export"""

    user_field_name = 'user'

    class Meta:
        model = SummitAnket
        fields = USER_RESOURCE_FIELDS + (
            'name', 'code',
            # 'last_name', 'first_name',
            # 'phone_number',
            # 'country', 'region', 'city', 'responsible', 'image',
            'pastor', 'bishop', 'sotnik', 'date',
        )


def get_pastor(user):
    if user.hierarchy.level == 3:
        return user
    if user.master:
        if user.master.hierarchy.level == 3:
            return user.master
        else:
            return get_pastor(user.master)
    else:
        # print("no master, stop")
        pass


def get_bishop(user):
    if user.hierarchy.level == 4:
        return user
    if user.master:
        if user.master.hierarchy.level == 4:
            return user.master
        else:
            return get_bishop(user.master)
    else:
        # print("no master, stop")
        pass


def get_sot(user):
    if user.hierarchy.level == 2:
        return user
    if user.master:
        if user.master.hierarchy.level == 2:
            return user.master
        else:
            return get_sot(user.master)
    else:
        return None


def find_pastor(anket):
    user = anket.user
    pastor = get_pastor(user)
    bishop = get_bishop(user)
    if pastor:
        anket.pastor = pastor.short
    else:
        anket.pastor = ""
    if bishop:
        anket.bishop = bishop.short
    else:
        anket.bishop = ""
    anket.date = user.date_joined
    anket.department = ', '.join(user.department.values_list('title', flat=True))
    anket.save()


def find_sot(anket):
    user = anket.user
    sot = get_sot(user)
    if sot:
        anket.sotnik = sot.short
    else:
        anket.sotnik = ''
    anket.save()


def get_fields(anket):
    anket.name = anket.user.short
    anket.country = anket.user.country
    anket.region = anket.user.region
    anket.phone_number = anket.user.phone_number
    anket.first_name = anket.user.first_name
    anket.last_name = anket.user.last_name
    anket.city = anket.user.city
    if not anket.code:
        summit_id = 4000000 + anket.id
        summit_id_str = '0%i' % summit_id
        anket.code = summit_id_str
    find_pastor(anket)
    find_sot(anket)
    if anket.pastor:
        anket.responsible = anket.pastor
    elif anket.sotnik:
        anket.responsible = anket.sotnik
    else:
        anket.responsible = anket.bishop
    anket.image = "%s.jpg" % anket.code
    anket.save()
