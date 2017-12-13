# -*- coding: utf-8
from import_export import fields
from django.utils.translation import ugettext_lazy as _

from common.resources import CustomFieldsModelResource
from apps.payment.models import Payment


class PaymentResource(CustomFieldsModelResource):
    """For excel import/export"""
    purpose_type = fields.Field(attribute='deals__type')
    purpose_fio = fields.Field(attribute='deals__partnership__user__last_name')
    purpose_manager_fio = fields.Field(attribute='deals__partnership__responsible__last_name')
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
        return _('партнерские') if payment.purpose.type == 1 else _('десятина')

    def dehydrate_purpose_date(self, payment):
        return payment.purpose.date_created

    def dehydrate_manager(self, payment):
        if payment.manager:
            return '%s %s %s' % (payment.manager.last_name,
                                 payment.manager.first_name,
                                 payment.manager.middle_name)
        return ''

    def dehydrate_purpose_fio(self, payment):
        return '%s %s %s' % (payment.purpose.partnership.user.last_name,
                             payment.purpose.partnership.user.first_name,
                             payment.purpose.partnership.user.middle_name)

    def dehydrate_purpose_manager_fio(self, payment):
        if payment.purpose.responsible:
            return '%s %s %s' % (payment.purpose.responsible.last_name,
                                 payment.purpose.responsible.first_name,
                                 payment.purpose.responsible.middle_name)
        return ''
