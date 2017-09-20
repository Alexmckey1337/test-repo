# -*- coding: utf-8
from __future__ import unicode_literals

from import_export import fields

from common.resources import CustomFieldsModelResource
from payment.models import Payment


class PaymentResource(CustomFieldsModelResource):
    """For excel import/export"""
    purpose_type = fields.Field(attribute='deals__type')
    purpose_fio = fields.Field(attribute='deals_partnership__user__last_name')
    purpose_manager_fio = fields.Field(attribute='deals__partnership__responsible__user__last_name')
    purpose_date = fields.Field(attribute='deals__date_created')
    sent_date = fields.Field(attribute='sent_date')
    manager = fields.Field(attribute='manager__user__last_name')
    sum_str = fields.Field(attribute='sum')
    created_at = fields.Field(attribute='created_at__date')
    description = fields.Field(attribute='description')

    class Meta:
        model = Payment
        fields = (
            'purpose_fio', 'purpose_manager_fio', 'purpose_date', 'sent_date', 'manager', 'sum',
            'created_at', 'description', 'purpose_type'
        )

    def dehydrate_purpose_type(self, payment):
        return 'партнерские' if payment.purpose.type == 1 else 'десятина'

    def dehydrate_purpose_fio(self, payment):
        return '%s %s %s' % (payment.purpose.partnership.user.last_name,
                             payment.purpose.partnership.user.first_name,
                             payment.purpose.partnership.user.middle_name)

    def dehydrate_purpose_manager_fio(self, payment):
        if payment.purpose.responsible:
            return '%s %s %s' % (payment.purpose.responsible.user.last_name,
                                 payment.purpose.responsible.user.first_name,
                                 payment.purpose.responsible.user.middle_name)
        else:
            return ''

    def dehydrate_purpose_date(self, payment):
        return payment.purpose.date_created

    def dehydrate_manager(self, payment):
        if payment.manager:
            return '%s %s %s' % (payment.manager.last_name,
                                 payment.manager.first_name,
                                 payment.manager.middle_name)
        else:
            return ''
