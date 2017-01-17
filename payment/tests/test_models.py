# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from account.models import CustomUser
from partnership.models import Partnership, Deal
from payment.models import Payment, get_default_currency, Currency
from summit.models import SummitAnket


@pytest.mark.django_db
def test_get_default_currency_with_uah():
    currency = Currency.objects.get(code='uah')

    assert get_default_currency() == currency.id


@pytest.mark.django_db
def test_get_default_currency_without_uah(currency_factory):
    Currency.objects.all().delete()

    other_currency = currency_factory()

    assert get_default_currency() == other_currency.id


@pytest.mark.django_db
def test_get_default_currency_without_currencies():
    Currency.objects.all().delete()

    assert get_default_currency() is None


@pytest.mark.django_db
class TestPayment:
    def test__str__for_summit(self, summit_anket_payment, anket):
        assert summit_anket_payment.__str__() == '{}: {}'.format(
            summit_anket_payment.created_at.strftime('%d %B %Y %H:%M'),
            anket.__str__())

    def test__str__for_partner(self, partner_payment, partner):
        assert partner_payment.__str__() == '{}: {}'.format(
            partner_payment.created_at.strftime('%d %B %Y %H:%M'),
            partner.__str__())

    def test__str__for_deal(self, deal_payment, deal):
        assert deal_payment.__str__() == '{}: {}'.format(
            deal_payment.created_at.strftime('%d %B %Y %H:%M'),
            deal.__str__())

    def test__str__without_purpose(self, payment):
        assert payment.__str__() == '{}: UNKNOWN'.format(
            payment.created_at.strftime('%d %B %Y %H:%M'))

    def test_payer_for_summit(self, summit_anket_payment, user):
        assert isinstance(summit_anket_payment.purpose, SummitAnket)
        assert isinstance(summit_anket_payment.payer, CustomUser)
        assert summit_anket_payment.payer == user

    def test_payer_for_partner(self, partner_payment, user):
        assert isinstance(partner_payment.purpose, Partnership)
        assert isinstance(partner_payment.payer, CustomUser)
        assert partner_payment.payer == user

    def test_payer_for_deal(self, deal_payment, user):
        assert isinstance(deal_payment.purpose, Deal)
        assert isinstance(deal_payment.payer, CustomUser)
        assert deal_payment.payer == user

    def test_payer_for_other(self, payment_factory, user_factory):
        other_payment = payment_factory(purpose=user_factory())

        assert other_payment.payer is None

    def test_payer_without_purpose(self, payment):
        assert payment.payer is None

    def test_calculate_effective_sum(self, payment):
        assert payment.calculate_effective_sum() == payment.sum * payment.rate

    def test_update_effective_sum_with_save(self, payment):
        payment.sum = Decimal('100')
        payment.rate = Decimal('1.24')
        payment.update_effective_sum()
        assert payment.effective_sum == 124

    def test_update_effective_sum_without_save(self, payment):
        old_effective_sum = payment.effective_sum
        payment.sum = Decimal('100')
        payment.rate = Decimal('1.24')
        payment.update_effective_sum(save=False)
        pk = payment.id
        assert payment.effective_sum == 124
        assert Payment.objects.get(pk=pk).effective_sum == old_effective_sum

    def test_sum_str(self, payment_factory, currency_factory):
        cur1 = currency_factory(short_name='cur1')
        cur2 = currency_factory(short_name='cur2')
        payment = payment_factory(currency_sum=cur1, currency_rate=cur2)
        assert payment.sum_str == '200 cur1'

    def test_effective_sum_str(self, payment_factory, currency_factory):
        cur1 = currency_factory(short_name='cur1')
        cur2 = currency_factory(short_name='cur2')
        payment = payment_factory(currency_sum=cur1, currency_rate=cur2, rate=Decimal(2))
        assert payment.effective_sum_str == '400 cur2'


@pytest.mark.django_db
class TestCurrency:
    def test__str__(self, currency):
        assert currency.__str__() == 'Currency (100 cur.)'

    def test__str__incorrect(self, currency):
        currency.output_format = '{incorrect_key}'
        assert currency.__str__() == "Currency (invalid format 'incorrect_key')"

    def test_clean_valid(self, currency):
        currency.clean()

    def test_clean_invalid(self, currency):
        with pytest.raises(ValidationError):
            currency.output_format = '{error}{value}'
            currency.clean()

    def test_output_dict(self, currency):
        assert currency.output_dict() == {'name': 'Currency', 'short_name': 'cur.', 'symbol': 'c'}
