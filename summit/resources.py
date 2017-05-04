# -*- coding: utf-8
from __future__ import unicode_literals

from django.utils import six

from account.resources import UserResource, USER_RESOURCE_FIELDS, UserMetaclass
from .models import SummitAnket


class SummitAnketResource(six.with_metaclass(UserMetaclass, UserResource)):
    """For excel import/export"""

    user_field_name = 'user'

    class Meta:
        model = SummitAnket
        fields = USER_RESOURCE_FIELDS + (
            'name', 'code',
            'pastor', 'bishop', 'sotnik', 'date',
        )
