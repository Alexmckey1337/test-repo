# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from payment.models import get_default_currency, AbstractPaymentPurpose
from summit.managers import AnketManager


@python_2_unicode_compatible
class SummitType(models.Model):
    """
    Type of the summit.
    """
    #: Title of the summit
    title = models.CharField(max_length=100, verbose_name='Название саммита')
    #: Club name of the summit.
    club_name = models.CharField(_('Club name'), max_length=30, blank=True)
    #: Summit image
    image = models.ImageField(upload_to='summit_type/images/', blank=True)
    #: Code of the summit type. Is an identifier for a summit_type.
    #: By code we can find the summit_type.
    code = models.SlugField(_('Code'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('Summit Type')
        verbose_name_plural = _('Summits Types')

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''


@python_2_unicode_compatible
class Summit(models.Model):
    #: Start date of the summit
    start_date = models.DateField()
    #: End date of the summit
    end_date = models.DateField()
    #: Summit type
    type = models.ForeignKey('SummitType', related_name='summits', blank=True, null=True)
    #: Display name
    description = models.CharField(max_length=255, verbose_name='Описание',
                                   blank=True, null=True)
    #: Code of the summit. Is an identifier for a summit.
    #: By code we can find the summit.
    code = models.SlugField(_('Code'), max_length=255, blank=True)
    #: Full cost of the summit.
    full_cost = models.DecimalField(_('Full cost'), max_digits=12, decimal_places=0,
                                    default=Decimal('0'))
    #: Special cost of the summit. If user is member of this summit type then he
    #: has discount for this summit.
    special_cost = models.DecimalField(_('Special cost'), max_digits=12, decimal_places=0,
                                       blank=True, null=True)
    #: Currency of full_cost and special_cost
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency'),
                                 default=get_default_currency, null=True)
    #: Template for sending tickets. This template using in dbmail.
    mail_template = models.ForeignKey('dbmail.MailTemplate', related_name='summits',
                                      verbose_name=_('Mail template'),
                                      null=True, blank=True)

    class Meta:
        ordering = ('type',)
        verbose_name = _('Summit')
        verbose_name_plural = _('Summits')

    def __str__(self):
        return '%s %s' % (self.type.title, self.start_date)

    def clean(self):
        """
        Validate a summit costs.

        If special cost is exist then the special cost must be less then full cost.
        """
        if self.special_cost is not None and self.full_cost <= self.special_cost:
            raise ValidationError(_('Special cost must be less then full cost'))

    @property
    def consultants(self):
        """
        Return list of the summit consultants

        :return: QuerySet
        """
        return self.ankets.filter(role__gte=SummitAnket.CONSULTANT)

    @property
    def title(self):
        return self.type.title

    @property
    def club_name(self):
        return self.type.club_name


class CustomUserAbstract(models.Model):
    # cloned the user when creating anket
    name = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    pastor = models.CharField(max_length=255, blank=True)
    bishop = models.CharField(max_length=255, blank=True)
    sotnik = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=date.today)
    department = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=255, blank=True)
    responsible = models.CharField(max_length=255, blank=True)
    image = models.CharField(max_length=12, blank=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class SummitAnket(CustomUserAbstract, AbstractPaymentPurpose):
    user = models.ForeignKey('account.CustomUser', related_name='summit_ankets')
    summit = models.ForeignKey('Summit', related_name='ankets', verbose_name='Саммит',
                               blank=True, null=True)

    #: The amount paid for the summit
    value = models.DecimalField(_('Paid amount'), max_digits=12, decimal_places=0,
                                default=Decimal('0'), editable=False)
    description = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=8, blank=True)

    retards = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)

    ticket = models.FileField(_('Ticket'), upload_to='tickets', null=True, blank=True)

    visited = models.BooleanField(default=False)

    VISITOR = settings.SUMMIT_ANKET_ROLES['visitor']
    CONSULTANT = settings.SUMMIT_ANKET_ROLES['consultant']
    SUPERVISOR = settings.SUMMIT_ANKET_ROLES['supervisor']

    ROLES = (
        (VISITOR, _('Visitor')),
        (CONSULTANT, _('Consultant')),
        (SUPERVISOR, _('Supervisor')),
    )
    role = models.PositiveSmallIntegerField(_('Summit Role'), choices=ROLES, default=VISITOR)

    summit_consultants = models.ManyToManyField(
        'summit.Summit', related_name='consultant_ankets',
        through='summit.SummitUserConsultant', through_fields=('user', 'summit'))

    #: Payments of the current anket
    payments = GenericRelation('payment.Payment', related_query_name='summit_ankets')

    objects = AnketManager()

    class Meta:
        ordering = ('summit__type', '-summit__start_date')
        unique_together = (('user', 'summit'),)

    def __str__(self):
        return '%s %s %s' % (self.user.fullname, self.summit.type.title, self.summit.start_date)

    @property
    def total_payed(self):
        return self.payments.aggregate(value=Sum('effective_sum'))['value']

    @property
    def currency(self):
        return self.summit.currency

    def calculate_value(self):
        payments = self.payments.filter(currency_rate=self.currency)
        # for payment in payments:
        #     payment.update_effective_sum(save=True)
        if self.payments.exclude(currency_rate=self.currency).exists():
            # TODO logging
            pass

        # payments.refresh_from_db()
        if payments.exists():
            value = payments.aggregate(value=Sum('effective_sum'))['value']
        else:
            value = 0
        return value

    def update_after_cancel_payment(self):
        self.update_value()

    update_after_cancel_payment.alters_data = True

    def update_value(self):
        self.value = self.calculate_value()
        self.save()

    update_value.alters_data = True

    @property
    def is_member(self):
        """
        Verification that the user is member of summit type.

        :return: boolean
        """
        summit_type = self.summit.type
        return summit_type.summits.filter(ankets__visited=True, ankets__user=self.user).exists()

    @property
    def is_full_paid(self):
        """
        Verification that the user paid for the summit.

        :return: boolean
        """
        if self.is_member and self.summit.special_cost is not None:
            return self.summit.special_cost <= self.total_payed
        else:
            return self.summit.full_cost <= self.total_payed


@python_2_unicode_compatible
class AnketEmail(models.Model):
    anket = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='emails',
                              verbose_name=_('Anket'))
    #: Email of recipient user
    recipient = models.CharField(_('Email'), max_length=255)

    subject = models.CharField(_('Subject'), max_length=255, blank=True)
    text = models.TextField(_('Text'), blank=True)
    html = models.TextField(_('HTML text'), blank=True)
    error_message = models.TextField(_('Error message'), blank=True)
    is_success = models.BooleanField(_('Is success'), default=True)
    attach = models.FileField(_('Attach'), upload_to='tickets', null=True, blank=True)

    created_at = models.DateTimeField(_('Date created'), auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.created_at, self.anket)

    class Meta:
        ordering = ('-created_at', 'anket')
        verbose_name = _('Anket email')
        verbose_name_plural = _('Anket emails')


@python_2_unicode_compatible
class SummitLesson(models.Model):
    #: Summit to which the lesson
    summit = models.ForeignKey('summit.Summit', on_delete=models.CASCADE, related_name='lessons',
                               related_query_name='lessons', verbose_name=_('Summit'))
    #: List of the users who is view this lesson
    viewers = models.ManyToManyField('summit.SummitAnket', related_name='all_lessons',
                                     verbose_name=_('Viewers'))
    #: Lesson name
    name = models.CharField(_('Name'), max_length=255)

    def __str__(self):
        return '{}: {}'.format(self.summit, self.name)

    class Meta:
        ordering = ('summit', 'name')
        verbose_name = _('Summit lesson')
        verbose_name_plural = _('Summit lessons')
        unique_together = ('name', 'summit')


@python_2_unicode_compatible
class SummitUserConsultant(models.Model):
    consultant = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='consultees',
                                   limit_choices_to={'role__gte': SummitAnket.CONSULTANT},
                                   verbose_name=_('Consultant'))
    user = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='consultants',
                             verbose_name=_('User'))
    summit = models.ForeignKey('summit.Summit', on_delete=models.CASCADE, related_name='consultees',
                               verbose_name=_('Summit'))

    def __str__(self):
        return '{}: {} is consultant for {}'.format(self.summit, self.consultant, self.user)

    class Meta:
        verbose_name = _('Summit consultant')
        verbose_name_plural = _('Summit consultants')
        unique_together = ('user', 'summit')

    def clean(self):
        if self.summit != self.user.summit:
            raise ValidationError(_('Этот пользователь не участвует в данном саммите.'))
        if self.summit != self.consultant.summit:
            raise ValidationError(_('Этот пользователь не является консультантом на данном саммите.'))


@python_2_unicode_compatible
class SummitAnketNote(models.Model):
    summit_anket = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='notes',
                                     verbose_name=_('Summit anket'))
    owner = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, related_name='notes',
                              null=True, blank=True, verbose_name=_('Owner of note'))

    text = models.CharField(_('Note'), max_length=1000)

    date_created = models.DateTimeField(_('Datetime created'), auto_now_add=True)

    def __str__(self):
        return self.short_text

    @property
    def short_text(self):
        return '{}...'.format(self.text[:47]) if len(self.text) > 50 else self.text

    @property
    def owner_name(self):
        return self.owner.fullname

    class Meta:
        verbose_name = _('Summit Anket Note')
        verbose_name_plural = _('Summit Anket Notes')
        ordering = ('-date_created',)
