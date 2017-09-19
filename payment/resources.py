# -*- coding: utf-8
from __future__ import unicode_literals

from import_export import fields

from common.resources import CustomFieldsModelResource
from payment.models import Payment


class PaymentResource(CustomFieldsModelResource):
    """For excel import/export"""
    purpose_fio = fields.Field(attribute='deals__partnership__user__last_name')
    purpose_manager_fio = fields.Field(attribute='deals__partnership__responsible__user__last_name')
    purpose_date = fields.Field(attribute='deals__date_created')
    sent_date =  fields.Field(attribute='sent_date')
    manager = fields.Field(attribute='manager__user__last_name')
    sum_str = fields.Field(attribute='sum')
    created_at = fields.Field(attribute='created_at')
    description = fields.Field(attribute='description')
    purpose_type = fields.Field(attribute='deals__type')

    user_field_name = 'user'

    class Meta:
        model = Payment
        fields = (
            'sum', 'rate'
        )
