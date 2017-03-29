# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from payment.managers import PaymentManager


def get_default_currency():
    if Currency.objects.filter(code='uah').exists():
        return Currency.objects.get(code='uah').id
    if Currency.objects.exists():
        return Currency.objects.first().id
    return None


class AbstractPaymentPurpose(models.Model):
    class Meta:
        abstract = True

    def update_after_cancel_payment(self):
        pass

    update_after_cancel_payment.alters_data = True

    def update_value(self):
        pass

    update_value.alters_data = True


@python_2_unicode_compatible
class Currency(models.Model):
    #: Name of currency, e.g. Dollar USA, Гривня, Euro, Рубль
    name = models.CharField(_('Name'), max_length=50)
    #: Code
    code = models.SlugField(_('Code'), max_length=8, unique=True)
    #: Short name of currency, e.g. usd, uah, eur, rur
    short_name = models.CharField(_('Short name'), max_length=8)
    #: Currency symbol, e.g. $, ₴, €, ₽
    symbol = models.CharField(_('Symbol'), max_length=8, blank=True)
    #: output format, e.g. '{symbol}{value}' -> '$100', '{value} {short_name}' -> '1000 uah'
    output_format = models.CharField(_('Output format'), max_length=255,
                                     help_text=_('Possible values: <br /><br />'
                                                 '{value} — sum, <br />'
                                                 '{symbol} — currency symbol, <br />'
                                                 '{short_name} — short name of currency, <br />'
                                                 '{name} — full name of currency'))

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    def clean(self):
        output_eg = self.output_dict()
        output_eg['value'] = 100
        try:
            self.output_format.format(**output_eg)
        except KeyError as err:
            raise ValidationError({
                'output_format': ValidationError(
                    _('Invalid output format: %(err)s'), code='invalid_output_format', params={'err': err})})

    def __str__(self):
        """
        Example:
        >>> n, s, f = 'Гривна', 'грн.', '{name}: {symbol}{value} {short_name}'
        >>> currency = Currency.objects.create(name=n, short_name=s, code='uah', symbol='₴', output_format=f)
        >>> print(currency)
        'Гривна (Гривна: ₴100 грн.)'

        :return: str
        """
        output_eg = self.output_dict()
        output_eg['value'] = 100
        try:
            return '{} ({})'.format(self.name, self.output_format.format(**output_eg))
        except KeyError as err:
            return '{} (invalid format {})'.format(self.name, err)

    def output_dict(self):
        """
        Return dict with keys == (name, short_name, symbol) for output_format

        Example:
        >>> n, s, f = 'Гривна', 'грн.', '{name}: {symbol}{value} {short_name}'
        >>> currency = Currency.objects.create(name=n, short_name=s, code='uah', symbol='₴', output_format=f)
        >>> d = currency.output_dict()
        >>> d
        {'name': 'Гривна', 'short_name': 'грн.', 'symbol': '₴'}

        :return: dict
        """
        return {
            'name': self.name,
            'short_name': self.short_name,
            'symbol': self.symbol or ''
        }


@python_2_unicode_compatible
class Payment(models.Model):
    #: Sum of the payment
    sum = models.DecimalField(_('Sum'), max_digits=12, decimal_places=0,
                              default=Decimal('0'))
    #: Currency of sum
    currency_sum = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency of sum'),
                                     default=get_default_currency, null=True,
                                     related_name='sum_payments')
    #: Currency relative to which there is conversion, currency_rate == purpose.currency
    #: Auto create as: Payment.objects.create(..., purpose=purpose, current_rate=purpose.currency),
    currency_rate = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, editable=False,
                                      default=get_default_currency, null=True,
                                      verbose_name=_('Rate currency'),
                                      related_name='rate_payments')
    #: Rate of currency
    rate = models.DecimalField(_('Rate'), max_digits=12, decimal_places=3, default=Decimal(1))
    #: Sum of the payment
    effective_sum = models.DecimalField(_('Effective sum'), max_digits=12, decimal_places=3,
                                        null=True, blank=True, editable=False)
    #: Comment for payment, such as the purpose of payment
    description = models.TextField(_('Description'), blank=True)
    #: Date and time when the payment has been created
    created_at = models.DateTimeField(_('Date created'), default=timezone.now, editable=False)
    #: Date  when the payment has been sent
    sent_date = models.DateField(_('Sent date'), default=timezone.now)
    #: The manager who received payment
    manager = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, related_name='checks',
                                null=True, blank=True, verbose_name=_('Manager'))

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True,
                                     limit_choices_to={'model__in': ('summitanket', 'partnership', 'deal')})
    object_id = models.PositiveIntegerField(blank=True, null=True)
    #: Purpose of payment
    purpose = GenericForeignKey()

    objects = PaymentManager()

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    @property
    def sum_str(self):
        format_data = self.currency_sum.output_dict()
        format_data['value'] = self.sum
        return self.currency_sum.output_format.format(**format_data)

    @property
    def effective_sum_str(self):
        format_data = self.currency_rate.output_dict()
        format_data['value'] = self.effective_sum
        return self.currency_rate.output_format.format(**format_data)

    def calculate_effective_sum(self):
        return self.sum * self.rate

    def update_effective_sum(self, save=True):
        self.effective_sum = self.calculate_effective_sum()
        if save:
            self.save(update_eff_sum=False)

    update_effective_sum.alters_data = True

    def save(self, *args, **kwargs):
        if not self.effective_sum or kwargs.get('update_eff_sum', True):
            self.update_effective_sum(save=False)
        if self.purpose and hasattr(self.purpose, 'currency'):
            self.currency_rate = self.purpose.currency
        if 'update_eff_sum' in kwargs:
            kwargs.pop('update_eff_sum')
        super(Payment, self).save(*args, **kwargs)
        if hasattr(self.purpose, 'update_value') and callable(self.purpose.update_value):
            # TODO не обрабатывает изменение (не пересчитывает предыдущего purpose, только нового)
            self.purpose.update_value()

    def get_data_for_deal_purpose_update(self):
        old = {
            'purpose': self.purpose,
            'sum': self.sum,
            'rate': self.rate,
            'object_id': self.object_id
        }
        return old

    def __str__(self):
        return '{}: {}'.format(self.created_at.strftime('%d %B %Y %H:%M'), self.purpose or 'UNKNOWN')

    @property
    def payer(self):
        """
        The user who made the payment.

        :return: CustomUser or None if content_type is not one of (SummitAnket, Partnership, Deal)
        """
        if not self.content_type:
            return None
        if self.content_type.model in ('summitanket', 'partnership'):
            return self.purpose.user
        if self.content_type.model == 'deal':
            return self.purpose.partnership.user
        return None
