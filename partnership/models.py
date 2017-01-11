# -*- coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict
from datetime import date
from decimal import Decimal

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.db.models import Sum, Count
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from payment.models import Payment, get_default_currency


@python_2_unicode_compatible
class Partnership(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='partnership')
    value = models.DecimalField(max_digits=12, decimal_places=0,
                                default=Decimal('0'))
    #: Currency of value
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency'),
                                 default=get_default_currency, null=True)
    date = models.DateField(default=date.today)
    need_text = models.CharField(_('Need text'), max_length=300, blank=True)

    is_active = models.BooleanField(_('Is active?'), default=True)

    DIRECTOR, SUPERVISOR, MANAGER, PARTNER = 0, 1, 2, 3
    LEVELS = (
        (DIRECTOR, _('Director')),
        (SUPERVISOR, _('Supervisor')),
        (MANAGER, _('Manager')),
        (PARTNER, _('Partner')),
    )
    level = models.PositiveSmallIntegerField(_('Level'), choices=LEVELS, default=PARTNER)

    responsible = models.ForeignKey('self', related_name='disciples', limit_choices_to={'level__lte': MANAGER},
                                    null=True, blank=True, on_delete=models.SET_NULL)

    #: Payments of the current partner that do not relate to deals of partner
    extra_payments = GenericRelation('payment.Payment', related_query_name='partners')

    def __str__(self):
        return self.fullname

    @property
    def deal_payments(self):
        """
        Payments for all deals of the current partner

        :return: QuerySet
        """
        return Payment.objects.filter(
            content_type__model='deal',
            object_id__in=self.deals.values_list('id', flat=True))

    @property
    def payments(self):
        """
        All payments of the current partner

        :return: QuerySet
        """
        return Payment.objects.filter((Q(content_type__model='deal') &
                                       Q(object_id__in=self.deals.values_list('id', flat=True))) |
                                      (Q(content_type__model='partnership') &
                                       Q(object_id=self.id)))

    @property
    def is_responsible(self):
        return self.level <= Partnership.MANAGER

    @property
    def fullname(self):
        return self.user.fullname

    @property
    def common(self):
        return ['Пользователь', 'Ответственный', 'Сумма', 'Количество сделок', 'Итого']

    @property
    def result_value(self):
        return self.deals.aggregate(sum_deals=Sum('value'))['sum_deals']

    @property
    def disciples_result_value(self):
        return self.disciples.aggregate(sum_deals=Sum('deals__value'))['sum_deals']

    @property
    def deals_count(self):
        return self.deals.count()

    @property
    def disciples_count(self):
        return self.disciples.aggregate(count=Count('deals'))['count']

    #
    # @property
    # def count(self):
    #     return self.deals_count

    @property
    def done_deals_count(self):
        return self.deals.filter(done=True).count()

    @property
    def undone_deals_count(self):
        return self.deals.filter(done=False, expired=False).count()

    @property
    def expired_deals_count(self):
        return self.deals.filter(expired=True).count()

    @property
    def done_deals(self):
        return self.deals.filter(done=True)

    @property
    def undone_deals(self):
        return self.deals.filter(done=False, expired=False)

    @property
    def expired_deals(self):
        return self.deals.filter(expired=True)


@python_2_unicode_compatible
class Deal(models.Model):
    value = models.DecimalField(max_digits=12, decimal_places=0,
                                default=Decimal('0'))
    #: Currency of value
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency'),
                                 editable=False, null=True,
                                 default=get_default_currency)

    partnership = models.ForeignKey('partnership.Partnership', related_name="deals")
    description = models.TextField(blank=True)
    done = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

    date_created = models.DateField(null=True, blank=True, default=date.today)
    date = models.DateField(null=True, blank=True)

    payments = GenericRelation('payment.Payment', related_query_name='deals')

    class Meta:
        ordering = ('date_created',)

    def __str__(self):
        return "%s : %s" % (self.partnership, self.date)

    def save(self, *args, **kwargs):
        if not self.id and self.partnership:
            self.currency = self.partnership.currency
        super(Deal, self).save(*args, **kwargs)

    @property
    def month(self):
        if self.date_created:
            return '{}.{}'.format(self.date_created.year, self.date_created.month)
        return ''
