# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from partnership.managers import DealManager, PartnerManager
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

    DIRECTOR = settings.PARTNER_LEVELS['director']
    SUPERVISOR = settings.PARTNER_LEVELS['supervisor']
    MANAGER = settings.PARTNER_LEVELS['manager']
    PARTNER = settings.PARTNER_LEVELS['partner']

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

    objects = PartnerManager()

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
        return self.deals.\
            base_queryset().\
            annotate_total_sum().\
            filter(done=True) \
            .order_by('-date_created')

    @property
    def undone_deals(self):
        return self.deals.\
            base_queryset().\
            annotate_total_sum().\
            filter(done=False, expired=False) \
            .order_by('-date_created')

    @property
    def expired_deals(self):
        return self.deals.\
            base_queryset().\
            annotate_total_sum().\
            filter(expired=True) \
            .order_by('-date_created')


@python_2_unicode_compatible
class Deal(models.Model):
    value = models.DecimalField(max_digits=12, decimal_places=0,
                                default=Decimal('0'))
    #: Currency of value
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency'),
                                 null=True,
                                 default=get_default_currency)

    partnership = models.ForeignKey('partnership.Partnership', related_name="deals")
    description = models.TextField(blank=True)
    done = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

    date_created = models.DateField(null=True, blank=True, default=date.today)
    date = models.DateField(null=True, blank=True)

    payments = GenericRelation('payment.Payment', related_query_name='deals')

    objects = DealManager()

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

    @property
    def total_payed(self):
        return self.payments.aggregate(total_payed=Coalesce(Sum('effective_sum'), Value(0)))['total_payed']

    @property
    def user(self):
        return self.partnership.user
