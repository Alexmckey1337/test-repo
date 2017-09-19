# -*- coding: utf-8
from __future__ import unicode_literals

from import_export import fields

from common.resources import CustomFieldsModelResource
from payment.models import Payment


class PaymentResource(CustomFieldsModelResource):
    """For excel import/export"""
    sum = fields.Field(attribute='sum')
    rate = fields.Field(attribute='rate')

    user_field_name = 'user'

    class Meta:
        model = Payment
        fields = (
            'sum', 'rate'
        )
