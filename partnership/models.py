# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from analytics.decorators import log_change_payment
from analytics.models import LogModel
from partnership.managers import DealManager, PartnerManager
from payment.models import Payment, get_default_currency, AbstractPaymentPurpose


@python_2_unicode_compatible
class PartnerRole(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='partner_role')

    DIRECTOR = settings.PARTNER_LEVELS['director']
    SUPERVISOR = settings.PARTNER_LEVELS['supervisor']
    MANAGER = settings.PARTNER_LEVELS['manager']

    LEVELS = (
        (DIRECTOR, _('Director')),
        (SUPERVISOR, _('Supervisor')),
        (MANAGER, _('Manager')),
    )
    level = models.PositiveSmallIntegerField(_('Level'), choices=LEVELS)
    plan = models.DecimalField(max_digits=12, decimal_places=0, blank=True,
                               verbose_name='Manager plan', null=True)

    def __str__(self):
        return '[{}] {}'.format(self.get_level_display(), self.fullname)


class PartnerRoleLog(models.Model):
    user = models.ForeignKey('account.CustomUser', related_name='partner_role_logs', editable=False)
    level = models.PositiveSmallIntegerField(_('Level'), editable=False)
    plan = models.DecimalField(max_digits=12, decimal_places=0, blank=True,
                               verbose_name='Manager plan', null=True, editable=False)
    deleted = models.BooleanField(_('Deleted?'), default=False)
    log_date = models.DateTimeField(_('Log date'), auto_now_add=True)

    class Meta:
        verbose_name = _('Partner role Log')
        verbose_name_plural = _('Partner role Logs')
        ordering = ('-log_date',)

    @classmethod
    def log_partner_role(cls, partner_role):
        cls.objects.create(
            user=partner_role.user,
            level=partner_role.level,
            plan=partner_role.plan,
        )

    @classmethod
    def delete_partner_role(cls, partner_role):
        cls.objects.create(
            user=partner_role.user,
            level=partner_role.level,
            plan=partner_role.plan,
            deleted=True,
        )


@python_2_unicode_compatible
class PartnershipAbstractModel(models.Model):
    value = models.DecimalField(max_digits=12, decimal_places=0,
                                default=Decimal('0'))
    #: Currency of value
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency'),
                                 default=get_default_currency, null=True)
    date = models.DateField(default=date.today)
    need_text = models.CharField(_('Need text'), max_length=600, blank=True)

    is_active = models.BooleanField(_('Is active?'), default=True)

    responsible = models.ForeignKey('account.CustomUser', related_name='partner_disciples', null=True, blank=True,
                                    on_delete=models.PROTECT)

    class Meta:
        abstract = True

    @property
    def value_str(self):
        """
        Partner value with currency.

        For example:
        partnership.value = 120
        partnership.currency.short_name = cur.
        partnership.currency.output_format = '{value} {short_name}'

        Then:
        partnership.value_str == '120 cur.'
        :return: str
        """
        format_data = self.currency.output_dict()
        format_data['value'] = self.value
        return self.currency.output_format.format(**format_data)


class Partnership(PartnershipAbstractModel, AbstractPaymentPurpose, LogModel):
    user = models.ForeignKey('account.CustomUser', related_name='partners')
    #: Payments of the current partner that do not relate to deals of partner
    extra_payments = GenericRelation('payment.Payment', related_query_name='partners')

    objects = PartnerManager()

    tracking_fields = (
        'value', 'currency', 'date', 'need_text', 'is_active', 'responsible'
    )

    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        now = timezone.now()
        current_deals = Deal.objects.filter(
            date_created__year=now.year, date_created__month=now.month,
            partnership=self, done=False)
        current_deals.update(responsible=self.responsible)

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

    def can_user_edit_payment(self, user):
        """
        Checking that the ``user`` can edit payment of current partner

        :param user:
        :return: True or False
        """
        return (user.is_partner_supervisor_or_high or
                (user.is_partner_manager and self.responsible == user))

    def payment_page_url(self):
        return reverse('payment-partner', kwargs={'pk': self.pk})

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
        return self.deals. \
            base_queryset(). \
            annotate_total_sum(). \
            filter(done=True) \
            .order_by('-date_created')

    @property
    def undone_deals(self):
        return self.deals. \
            base_queryset(). \
            annotate_total_sum(). \
            filter(done=False, expired=False) \
            .order_by('-date_created')

    @property
    def expired_deals(self):
        return self.deals. \
            base_queryset(). \
            annotate_total_sum(). \
            filter(expired=True) \
            .order_by('-date_created')


@python_2_unicode_compatible
class Deal(LogModel, AbstractPaymentPurpose):
    value = models.DecimalField(max_digits=12, decimal_places=0,
                                default=Decimal('0'))
    #: Currency of value
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT,
                                 verbose_name=_('Currency'),
                                 null=True,
                                 default=get_default_currency)

    partnership = models.ForeignKey('partnership.Partnership', related_name="deals")
    responsible = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,
                                    related_name='disciples_deals', editable=False,
                                    verbose_name=_('Responsible of partner'), null=True, blank=True)
    description = models.TextField(blank=True)
    done = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

    date_created = models.DateField(null=True, blank=True, default=date.today)
    date = models.DateField(null=True, blank=True)

    DONATION, TITHE = 1, 2
    DEAL_TYPE_CHOICES = (
        (DONATION, _('Donation')),
        (TITHE, _('Tithe'))
    )

    type = models.PositiveSmallIntegerField(_('Deal type'), choices=DEAL_TYPE_CHOICES, default=1)

    payments = GenericRelation('payment.Payment', related_query_name='deals')

    objects = DealManager()

    tracking_fields = ('done', 'value', 'currency', 'description', 'expired', 'date', 'date_created')

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return "%s : %s" % (self.partnership, self.date_created)

    def save(self, *args, **kwargs):
        if not self.id and self.partnership:
            self.currency = self.partnership.currency
            self.responsible = self.partnership.responsible
        super(Deal, self).save(*args, **kwargs)

    @log_change_payment(['done'])
    def update_after_cancel_payment(self, editor, payment):
        self.done = False
        self.save()

    update_after_cancel_payment.alters_data = True

    @property
    def partner_link(self):
        return self.partnership.user.link

    @property
    def value_str(self):
        """
        Deal value with currency.

        For example:
        deal.value = 120
        deal.currency.short_name = cur.
        deal.currency.output_format = '{value} {short_name}'

        Then:
        deal.value_str == '120 cur.'
        :return: str
        """
        format_data = self.currency.output_dict()
        format_data['value'] = self.value
        return self.currency.output_format.format(**format_data)

    def can_user_edit(self, user):
        """
        Checking that the ``user`` can edit current deal

        :param user:
        :return: True or False
        """
        return (user.is_partner_supervisor_or_high or
                (user.is_partner_manager and self.responsible.user == user))

    def can_user_edit_payment(self, user):
        """
        Checking that the ``user`` can edit payment of current deal

        :param user:
        :return: True or False
        """
        return self.can_user_edit(user)

    def payment_page_url(self):
        return reverse('payment-deal', kwargs={'pk': self.pk})

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


class PartnershipLogs(PartnershipAbstractModel):
    partner = models.ForeignKey('Partnership', related_name='partner', on_delete=models.PROTECT,
                                verbose_name=_('Partner'))
    responsible = models.ForeignKey('account.CustomUser', related_name='partner_disciples_logs',
                                    null=True, blank=True, on_delete=models.SET_NULL)

    log_date = models.DateTimeField(_('Log date'), auto_now_add=True)

    class Meta:
        verbose_name = _('Partnership Log')
        verbose_name_plural = _('Partnership Logs')
        ordering = ('-log_date',)

    def __str__(self):
        return 'Partner: %s. Log date: %s' % (self.partner, self.log_date.strftime('%Y.%m'))

    @classmethod
    def log_partner(cls, partner):
        cls.objects.create(
            value=partner.value,
            currency=partner.currency,
            date=partner.date,
            need_text=partner.need_text,
            is_active=partner.is_active,
            responsible=partner.responsible,
            partner=partner,
        )
