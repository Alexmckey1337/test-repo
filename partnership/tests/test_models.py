# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from datetime import datetime

import pytest


@pytest.mark.django_db
class TestPartnership:
    def test_partner_extra_payments(self, partner, payment_factory):
        payment_factory.create_batch(11, purpose=partner)
        assert partner.extra_payments.count() == 11

    def test__str__(self, partner):
        assert partner.__str__() == partner.fullname

    def test_partner_payments_without_deal_payments(self, partner, payment_factory):
        payment_factory.create_batch(11, purpose=partner)
        assert partner.payments.count() == 11

    def test_partner_payments_with_deal_payments(self, partner, payment_factory, deal_factory):
        deal1 = deal_factory(partnership=partner)
        deal2 = deal_factory(partnership=partner)
        payment_factory.create_batch(11, purpose=partner)  # count +11, = 11
        payment_factory.create_batch(2, purpose=deal1)  # count +2, = 13
        payment_factory.create_batch(3, purpose=deal2)  # count +3, = 16
        assert partner.payments.count() == 16

    def test_partner_deal_payments_with_deal_payments(self, partner, payment_factory, deal_factory):
        deal1 = deal_factory(partnership=partner)
        deal2 = deal_factory(partnership=partner)
        payment_factory.create_batch(11, purpose=partner)  # count +0, = 0
        payment_factory.create_batch(2, purpose=deal1)  # count +2, = 2
        payment_factory.create_batch(3, purpose=deal2)  # count +3, = 5
        assert partner.deal_payments.count() == 5

    @pytest.mark.parametrize(
        "level", range(4), ids=['director', 'supervisor', 'manager', 'partner'])
    def test_is_responsible(self, partner, level):
        partner.level = level
        partner.save()
        if level <= partner.__class__.MANAGER:
            assert partner.is_responsible
        else:
            assert not partner.is_responsible

    def test_full_name(self, partner, user):
        assert partner.fullname == user.fullname

    def test_done_deals_count(self, partner_with_deals):
        assert partner_with_deals.done_deals_count == 2

    def test_undone_deals_count(self, partner_with_deals):
        assert partner_with_deals.undone_deals_count == 5

    def test_expired_deals_count(self, partner_with_deals):
        assert partner_with_deals.expired_deals_count == 8

    def test_done_deals(self, partner_with_deals):
        assert [deal.done for deal in partner_with_deals.done_deals] == [True, True]

    def test_undone_deals(self, partner_with_deals):
        assert ([(deal.done, deal.expired) for deal in partner_with_deals.undone_deals] ==
                [(False, False) for _ in range(5)])

    def test_expired_deals(self, partner_with_deals):
        assert [deal.expired for deal in partner_with_deals.expired_deals] == [True for _ in range(8)]


@pytest.mark.django_db
class TestDeal:
    def test__str__(self, deal, partner):
        assert deal.__str__() == '{} : {}'.format(partner.__str__(), deal.date)

    def test_save_as_new(self, deal_factory, partner, currency):
        partner.currency = currency
        partner.save()

        new_deal = deal_factory.build(partnership=partner, currency=None)
        new_deal.save()

        assert new_deal.currency == currency

    def test_save_as_exist(self, deal, partner, currency):
        partner.currency = currency
        partner.save()

        deal.save()

        assert deal.currency != currency

    def test_value_str(self, deal):
        assert deal.value_str == '{} {}'.format(deal.value, deal.currency.short_name)

    def test_deal_payments(self, deal, payment_factory):
        payment_factory.create_batch(4, purpose=deal)

        assert deal.payments.count() == 4

    def test_month_with_date_created(self, deal_factory):
        deal = deal_factory(date_created=datetime(2000, 11, 20))
        assert deal.month == '2000.11'

    def test_month_without_date_created(self, deal):
        deal.date_created = None
        deal.save()
        assert deal.month == ''

    def test_total_payed_with_payments(self, deal, payment_factory):
        payment_factory.create_batch(4, purpose=deal, sum=11)

        assert deal.total_payed == 44

    def test_total_payed_without_payments(self, deal):
        assert deal.total_payed == 0
