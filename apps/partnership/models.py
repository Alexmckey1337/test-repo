from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.analytics.decorators import log_change_payment
from apps.analytics.models import LogModel
from apps.partnership.managers import DealManager, PartnerManager, ChurchDealManager
from apps.payment.models import Payment, get_default_currency, AbstractPaymentPurpose
from common import date_utils


class PartnerRole(models.Model):
    user = models.OneToOneField('account.CustomUser', on_delete=models.PROTECT, related_name='partner_role')

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
        return '[{}] {}'.format(self.get_level_display(), self.user.fullname)


class PartnerRoleLog(models.Model):
    user = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT, related_name='partner_role_logs',
                             editable=False)
    level = models.PositiveSmallIntegerField(_('Level'), editable=False)
    plan = models.DecimalField(max_digits=12, decimal_places=0, blank=True,
                               verbose_name='Manager plan', null=True, editable=False)
    deleted = models.BooleanField(_('Deleted?'), default=False)
    log_date = models.DateTimeField(_('Log date'), auto_now_add=True, db_index=True)

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


class PartnerGroup(models.Model):
    title = models.CharField(_('Partner group'), max_length=255)
    USER, CHURCH = 'user', 'church'
    TYPES = (
        (USER, _('User')),
        (CHURCH, _('Church')),
    )
    type = models.CharField(_('Type'), choices=TYPES, max_length=255, default=USER)

    def __str__(self):
        return self.title


class PartnershipAbstractModel(models.Model):
    value = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal('0'))
    #: Currency of value
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency'),
                                 default=get_default_currency, null=True)
    date = models.DateField(default=date_utils.today)
    need_text = models.CharField(_('Need text'), max_length=600, blank=True)

    is_active = models.BooleanField(_('Is active?'), default=True)

    responsible = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT, verbose_name=_('Responsible'),
                                    related_name='partner_disciples', null=True, blank=True)
    group = models.ForeignKey('partnership.PartnerGroup', on_delete=models.PROTECT, verbose_name=_('Group'),
                              related_name='partners', null=True, blank=True)
    UA, EU = 'UA', 'EU'
    TITLES = (
        (UA, 'UA'),
        (EU, 'EU'),
    )
    title = models.CharField(_('Partner title'), choices=TITLES, max_length=255, default=UA)

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
    user = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT, related_name='partners')
    #: Payments of the current partner that do not relate to deals of partner
    extra_payments = GenericRelation('payment.Payment', related_query_name='partners')

    objects = PartnerManager()

    tracking_fields = (
        'value', 'currency', 'date', 'need_text', 'is_active', 'responsible', 'group', 'title'
    )

    def __str__(self):
        return '{} ({})'.format(self.fullname, self.title) if self.title else self.fullname

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
        return self.deal_payments

    def can_user_edit_payment(self, user):
        """
        Checking that the ``user`` can edit payment of current partner

        :param user:
        :return: True or False
        """
        return (user.is_partner_supervisor_or_high or
                (user.is_partner_manager and self.responsible == user))

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

    @property
    def is_vip(self):
        vip_value = settings.DEFAULT_SITE_SETTINGS.\
            get('partners', {}).\
            get('vip_status', {}).\
            get(self.currency.code, -1)
        return self.value >= vip_value >= 0

    @property
    def is_ruby(self):
        if self.is_vip:
            return False
        vip_value = settings.DEFAULT_SITE_SETTINGS. \
            get('partners', {}). \
            get('ruby_status', {}). \
            get(self.currency.code, -1)
        return self.value >= vip_value >= 0

    @property
    def is_gold(self):
        if self.is_vip or self.is_ruby:
            return False
        vip_value = settings.DEFAULT_SITE_SETTINGS. \
            get('partners', {}). \
            get('gold_status', {}). \
            get(self.currency.code, -1)
        return self.value >= vip_value >= 0


class AbstractDeal(models.Model):
    partnership = None
    responsible = None
    value = models.DecimalField(max_digits=12, decimal_places=0,
                                default=Decimal('0'))
    #: Currency of value
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT,
                                 verbose_name=_('Currency'),
                                 null=True,
                                 default=get_default_currency)

    description = models.TextField(blank=True)
    done = models.BooleanField(default=False, help_text=_('Deal is done?'))
    expired = models.BooleanField(default=False)

    date_created = models.DateField(null=True, blank=True, default=date_utils.today)
    date = models.DateField(null=True, blank=True)

    DONATION, TITHE = 1, 2
    DEAL_TYPE_CHOICES = (
        (DONATION, _('Donation')),
        (TITHE, _('Tithe'))
    )

    type = models.PositiveSmallIntegerField(_('Deal type'), choices=DEAL_TYPE_CHOICES, default=DONATION)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s : %s" % (self.partnership, self.date_created)

    def save(self, *args, **kwargs):
        if not self.id and self.partnership:
            self.currency = self.partnership.currency
            self.responsible = self.partnership.responsible
        super().save(*args, **kwargs)

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

    @log_change_payment(['done'])
    def update_after_cancel_payment(self, editor, payment):
        self.done = False
        self.save()

    update_after_cancel_payment.alters_data = True

    @property
    def month(self):
        if self.date_created:
            return '{}.{}'.format(self.date_created.year, self.date_created.month)
        return ''


class Deal(AbstractDeal, LogModel, AbstractPaymentPurpose):
    partnership = models.ForeignKey('partnership.Partnership', on_delete=models.PROTECT, related_name="deals")
    responsible = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,
                                    related_name='disciples_deals', editable=False,
                                    verbose_name=_('Responsible of partner'), null=True, blank=True)

    payments = GenericRelation('payment.Payment', related_query_name='deals')

    objects = DealManager()

    tracking_fields = ('done', 'value', 'currency', 'description', 'expired', 'date', 'date_created')

    class Meta:
        ordering = ('-date_created',)

    @property
    def partner_link(self):
        return self.partnership.user.link

    def can_user_edit(self, user):
        """
        Checking that the ``user`` can edit current deal

        :param user:
        :return: True or False
        """
        return (user.is_partner_supervisor_or_high or
                (user.is_partner_manager and self.responsible == user))

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
    group = models.ForeignKey('partnership.PartnerGroup', on_delete=models.PROTECT,
                              related_name='partners_logs', null=True, blank=True)

    log_date = models.DateTimeField(_('Log date'), auto_now_add=True, db_index=True)

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
            group=partner.group,
            title=partner.title,
            partner=partner,
        )


class ChurchPartner(PartnershipAbstractModel, AbstractPaymentPurpose, LogModel):
    church = models.ForeignKey('group.Church', on_delete=models.PROTECT, related_name='partners')

    responsible = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT, verbose_name=_('Responsible'),
                                    related_name='church_partner_disciples', null=True, blank=True)
    group = models.ForeignKey('partnership.PartnerGroup', on_delete=models.PROTECT, verbose_name=_('Group'),
                              related_name='church_partners', null=True, blank=True)

    tracking_fields = (
        'value', 'currency', 'date', 'need_text', 'is_active', 'responsible', 'group', 'title'
    )

    def __str__(self):
        return '{} ({})'.format(self.church.get_title, self.title) if self.title else self.church.get_title


class ChurchDeal(AbstractDeal, LogModel, AbstractPaymentPurpose):
    partnership = models.ForeignKey('partnership.ChurchPartner', on_delete=models.PROTECT, related_name="deals")
    responsible = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                    related_name='partner_disciples_deals', editable=False,
                                    verbose_name=_('Responsible of partner'), null=True, blank=True)

    payments = GenericRelation('payment.Payment', related_query_name='church_deals')

    objects = ChurchDealManager()

    tracking_fields = ('done', 'value', 'currency', 'description', 'expired', 'date', 'date_created')

    class Meta:
        ordering = ('-date_created',)

    @property
    def partner_link(self):
        return self.partnership.church.link


class ChurchPartnerLog(PartnershipAbstractModel):
    partner = models.ForeignKey('ChurchPartner', related_name='logs', on_delete=models.PROTECT,
                                verbose_name=_('Partner'))
    responsible = models.ForeignKey('account.CustomUser', related_name='church_partner_disciples_logs',
                                    null=True, blank=True, on_delete=models.PROTECT)
    group = models.ForeignKey('partnership.PartnerGroup', on_delete=models.PROTECT,
                              related_name='church_partners_logs', null=True, blank=True)

    log_date = models.DateTimeField(_('Log date'), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('Church Partner Log')
        verbose_name_plural = _('Church Partner Logs')
        ordering = ('-log_date',)

    def __str__(self):
        return 'Church partner: %s. Log date: %s' % (self.partner, self.log_date.strftime('%Y.%m'))

    @classmethod
    def log_partner(cls, partner):
        cls.objects.create(
            value=partner.value,
            currency=partner.currency,
            date=partner.date,
            need_text=partner.need_text,
            is_active=partner.is_active,
            responsible=partner.responsible,
            group=partner.group,
            title=partner.title,
            partner=partner,
        )


class TelegramGroup(models.Model):
    title = models.CharField(_('Group Title'), max_length=255)  # CHAT_ID = -317988135
    join_url = models.URLField(_('Join url'))
    chat_id = models.CharField(_('Chat ID'), max_length=255)
    bot_address = models.CharField(_('Bot address'), max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Группа в Telegram'
        verbose_name_plural = 'Группы в Telegram'
        ordering = ('-id',)

    def __str__(self):
        return '%s' % self.title


class TelegramUser(models.Model):
    user = models.ForeignKey('account.CustomUser', related_name='telegram_users',
                             on_delete=models.PROTECT, verbose_name=_('Telegram User'))

    telegram_id = models.IntegerField(_('Telegram ID'))
    telegram_group = models.ForeignKey('TelegramGroup', related_name='telegram_users',
                                       verbose_name=_('Telegram Group'), on_delete=models.PROTECT)
    is_active = models.BooleanField(_('Is Active'), default=True)
    synced = models.BooleanField(_('Is synced?'), default=True)

    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'
        ordering = ('-id',)
        unique_together = ['user', 'telegram_id', 'telegram_group']

    def __str__(self):
        return '%s' % self.user
