# -*- coding: utf-8
from __future__ import unicode_literals

from django.utils import six

from apps.account.resources import USER_RESOURCE_FIELDS, UserResource, UserMetaclass
from apps.group.resources import ChurchResource, ChurchMetaclass, CHURCH_RESOURCE_FIELDS
from apps.partnership.models import Partnership, ChurchPartner


class PartnerResource(six.with_metaclass(UserMetaclass, UserResource)):
    """For excel import/export"""

    user_field_name = 'user'

    class Meta:
        model = Partnership
        fields = USER_RESOURCE_FIELDS + ('responsible', 'value')

    def dehydrate_responsible(self, partner):
        if not partner.responsible:
            return ''
        return partner.responsible.fullname

    def dehydrate_value(self, partner):
        return partner.value_str


class ChurchPartnerResource(six.with_metaclass(ChurchMetaclass, ChurchResource)):
    """For excel import/export"""

    church_field_name = 'church'

    class Meta:
        model = ChurchPartner
        fields = CHURCH_RESOURCE_FIELDS + ('responsible', 'value')

    def dehydrate_responsible(self, partner):
        if not partner.responsible:
            return ''
        return partner.responsible.fullname

    def dehydrate_value(self, partner):
        return partner.value_str
