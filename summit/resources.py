# -*- coding: utf-8
from __future__ import unicode_literals

from import_export import fields

from common.resources import CustomFieldsModelResource
from .models import SummitAnket


class SummitAnketResource(CustomFieldsModelResource):
    """For excel import/export"""
    full_name = fields.Field()
    e_ticket = fields.Field()
    email = fields.Field()
    phone_number = fields.Field()
    district = fields.Field()
    address = fields.Field()
    region = fields.Field()
    repentance_date = fields.Field()
    born_date = fields.Field()

    user_field_name = 'user'

    class Meta:
        model = SummitAnket
        fields = (
            'full_name', 'email', 'phone_number',
            'e_ticket',
            'district', 'address', 'region',
            'repentance_date', 'born_date',

            'hierarchy_title', 'responsible',
            'divisions_title', 'spiritual_level', 'city', 'country', 'department',
            'value', 'description',
            'code', 'ticket_status',
        )

    def dehydrate_spiritual_level(self, user):
        return user.get_spiritual_level_display()

    def dehydrate_full_name(self, profile):
        return profile.user.fullname

    def dehydrate_e_ticket(self, profile):
        if hasattr(profile, 'status'):
            return profile.status.reg_code_requested
        return False

    def dehydrate_district(self, profile):
        return profile.user.district

    def dehydrate_address(self, profile):
        return profile.user.address

    def dehydrate_region(self, profile):
        return profile.user.region

    def dehydrate_repentance_date(self, profile):
        return profile.user.repentance_date

    def dehydrate_born_date(self, profile):
        return profile.user.born_date

    def dehydrate_phone_number(self, profile):
        return profile.user.phone_number

    def dehydrate_email(self, profile):
        return profile.user.email


class SummitStatisticsResource(CustomFieldsModelResource):
    """For excel import/export"""
    full_name = fields.Field()
    phone_number = fields.Field()
    attended = fields.Field(attribute='attended')

    user_field_name = 'user'

    class Meta:
        model = SummitAnket
        fields = (
            'full_name', 'phone_number', 'attended',
            'responsible', 'department', 'code',
        )

    def dehydrate_full_name(self, profile):
        return profile.user.fullname

    def dehydrate_phone_number(self, profile):
        return profile.user.phone_number
    #
    # def dehydrate_attended(self, profile):
    #     subqs = SummitAttend.objects.filter(date=self.filter_date, anket=profile)
    #     return subqs.exists()
