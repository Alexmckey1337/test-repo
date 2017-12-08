# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from collections import namedtuple
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.utils import timezone

Level = namedtuple('Level', ['title', 'level'])
PARTNER_LEVELS = [Level(p[0], p[1]) for p in settings.PARTNER_LEVELS.items()]


@pytest.mark.urls('partnership.tests.urls')
@pytest.mark.django_db
class TestPartnership:
    def test_partner_extra_payments(self, partner, payment_factory):
        payment_factory.create_batch(11, purpose=partner)
        assert partner.extra_payments.count() == 11

    def test__str__(self, partner):
        assert partner.__str__() == '{} (UA)'.format(partner.fullname)

    def test_move_old_unclosed_deal_after_change_responsible(self, user_factory, partner_factory, deal_factory):
        responsible = user_factory()
        partner = partner_factory(responsible=responsible)  # autocreate deal
        deal_factory.create_batch(2, date_created=timezone.now() + timedelta(days=-32), partnership=partner)

        assert responsible.disciples_deals.count() == 3

        partner.responsible = user_factory()
        partner.save()

        assert responsible.disciples_deals.count() == 2

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

    def test_value_str(self, partner):
        assert partner.value_str == '{} {}'.format(partner.value, partner.currency.short_name)

    def test_payment_page_url(self, partner):
        assert partner.payment_page_url() == '/payment/partner/{}/'.format(partner.id)

    @pytest.mark.parametrize('with_responsible', [True, False], ids=['with_responsible', 'without_responsible'])
    @pytest.mark.parametrize('level', [p.level for p in PARTNER_LEVELS], ids=[p.title for p in PARTNER_LEVELS])
    def test_can_user_edit_payment(self, user_factory, partner_factory, partner_role_factory, level, with_responsible):
        responsible = user_factory() if with_responsible else None
        partner = partner_factory(responsible=responsible)
        editor = partner_role_factory(level=level)
        if level > settings.PARTNER_LEVELS['supervisor']:
            assert not partner.can_user_edit_payment(editor.user)
        else:
            assert partner.can_user_edit_payment(editor.user)

    @pytest.mark.parametrize('level', [p.level for p in PARTNER_LEVELS], ids=[p.title for p in PARTNER_LEVELS])
    def test_can_user_edit_payment_if_user_is_responsible(self, partner_factory, partner_role_factory, level):
        editor = partner_role_factory(level=level)
        partner = partner_factory(responsible=editor.user)
        if level > settings.PARTNER_LEVELS['manager']:
            assert not partner.can_user_edit_payment(editor.user)
        else:
            assert partner.can_user_edit_payment(editor.user)


@pytest.mark.urls('partnership.tests.urls')
@pytest.mark.django_db
class TestDeal:
    def test__str__(self, deal, partner):
        assert deal.__str__() == '{} : {}'.format(partner.__str__(), deal.date_created)

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

    def test_update_after_cancel_payment(self, user, deal_factory):
        deal = deal_factory(done=True)

        def __str__(self):
            return 'payment'

        assert deal.done
        deal.update_after_cancel_payment(editor=user, payment=type('Payment', (), {'id': 1, '__str__': __str__}))
        assert not deal.done

    def test_payment_page_url(self, deal):
        assert deal.payment_page_url() == '/payment/deal/{}/'.format(deal.id)

    @pytest.mark.parametrize('with_responsible', [True, False], ids=['with_responsible', 'without_responsible'])
    @pytest.mark.parametrize('level', [p.level for p in PARTNER_LEVELS], ids=[p.title for p in PARTNER_LEVELS])
    def test_can_user_edit(self, deal, user_factory, partner_role_factory, partner_factory, level, with_responsible):
        responsible = user_factory() if with_responsible else None
        deal.responsible = responsible
        deal.save()
        user_role = partner_role_factory(level=level)
        editor = partner_factory(user=user_role.user, responsible=responsible)
        if level > settings.PARTNER_LEVELS['supervisor']:
            assert not deal.can_user_edit(editor.user)
        else:
            assert deal.can_user_edit(editor.user)

    @pytest.mark.parametrize('level', [p.level for p in PARTNER_LEVELS], ids=[p.title for p in PARTNER_LEVELS])
    def test_can_user_edit_if_user_is_responsible(self, deal, partner_role_factory, level):
        editor = partner_role_factory(level=level)
        deal.responsible = editor.user
        deal.save()
        if level > settings.PARTNER_LEVELS['manager']:
            assert not deal.can_user_edit(editor.user)
        else:
            assert deal.can_user_edit(editor.user)

    @pytest.mark.parametrize('with_responsible', [True, False], ids=['with_responsible', 'without_responsible'])
    @pytest.mark.parametrize('level', [p.level for p in PARTNER_LEVELS], ids=[p.title for p in PARTNER_LEVELS])
    def test_can_user_edit_payment(self, deal, user_factory, partner_role_factory, partner_factory, level,
                                   with_responsible):
        responsible = user_factory() if with_responsible else None
        deal.responsible = responsible
        deal.save()

        user_role = partner_role_factory(level=level)
        editor = partner_factory(user=user_role.user, responsible=responsible)
        if level > settings.PARTNER_LEVELS['supervisor']:
            assert not deal.can_user_edit_payment(editor.user)
        else:
            assert deal.can_user_edit_payment(editor.user)

    @pytest.mark.parametrize('level', [p.level for p in PARTNER_LEVELS], ids=[p.title for p in PARTNER_LEVELS])
    def test_can_user_edit_payment_if_user_is_responsible(self, deal, partner_role_factory, level):
        editor = partner_role_factory(level=level)
        deal.responsible = editor.user
        deal.save()
        if level > settings.PARTNER_LEVELS['manager']:
            assert not deal.can_user_edit_payment(editor.user)
        else:
            assert deal.can_user_edit_payment(editor.user)
