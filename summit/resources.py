# -*- coding: utf-8
from __future__ import unicode_literals

from import_export import fields

from common.resources import CustomFieldsModelResource
from summit.models import SummitAnket


class SummitAnketResource(CustomFieldsModelResource):
    """For excel import/export"""
    full_name = fields.Field(attribute='full_name')
    e_ticket = fields.Field(attribute='status__reg_code_requested')
    reg_code = fields.Field(attribute='reg_code')
    email = fields.Field(attribute='user__email')
    phone_number = fields.Field(attribute='user__phone_number')
    district = fields.Field(attribute='user__district')
    address = fields.Field(attribute='user__address')
    region = fields.Field(attribute='user__region')
    repentance_date = fields.Field(attribute='user__repentance_date')
    born_date = fields.Field(attribute='user__born_date')

    user_field_name = 'user'

    class Meta:
        model = SummitAnket
        fields = (
            'full_name', 'email', 'phone_number',
            'e_ticket',
            'district', 'address', 'region',
            'repentance_date', 'born_date',
            'reg_code',

            'hierarchy_title', 'responsible',
            'divisions_title', 'spiritual_level', 'city', 'country', 'department',
            'value', 'description',
            'code', 'ticket_status',
        )

    def dehydrate_spiritual_level(self, user):
        return user.get_spiritual_level_display()

    def dehydrate_full_name(self, user):
        return user.full_name

    def export(self, queryset=None, *args, **kwargs):
        self.custom_export_fields = kwargs.get('custom_export_fields') + ['reg_code']
        return super(CustomFieldsModelResource, self).export(queryset=queryset, *args, **kwargs)


class SummitStatisticsResource(CustomFieldsModelResource):
    """For excel import/export"""
    full_name = fields.Field(attribute='full_name')
    phone_number = fields.Field(attribute='user__phone_number')
    attended = fields.Field(attribute='attended')

    user_field_name = 'user'

    class Meta:
        model = SummitAnket
        fields = (
            'full_name', 'phone_number', 'attended',
            'responsible', 'department', 'code',
        )
