# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest

from partnership.factories import PartnerFactory, DealFactory
from payment.factories import PaymentFactory


@pytest.mark.django_db
def test_partner_extra_payments():
    partner = PartnerFactory()
    PaymentFactory.create_batch(11, purpose=partner)
    assert partner.extra_payments.count() == 11


@pytest.mark.django_db
def test_partner_payments_without_deal_payments():
    partner = PartnerFactory()
    PaymentFactory.create_batch(11, purpose=partner)
    assert partner.payments.count() == 11


@pytest.mark.django_db
def test_partner_payments_with_deal_payments():
    partner = PartnerFactory()
    deal1 = DealFactory(partnership=partner)
    deal2 = DealFactory(partnership=partner)
    PaymentFactory.create_batch(11, purpose=partner)  # count +11, = 11
    PaymentFactory.create_batch(2, purpose=deal1)  # count +2, = 13
    PaymentFactory.create_batch(3, purpose=deal2)  # count +3, = 16
    assert partner.payments.count() == 16


@pytest.mark.django_db
def test_partner_deal_payments_with_deal_payments():
    partner = PartnerFactory()
    deal1 = DealFactory(partnership=partner)
    deal2 = DealFactory(partnership=partner)
    PaymentFactory.create_batch(11, purpose=partner)  # count +0, = 0
    PaymentFactory.create_batch(2, purpose=deal1)  # count +2, = 2
    PaymentFactory.create_batch(3, purpose=deal2)  # count +3, = 5
    assert partner.deal_payments.count() == 5


@pytest.mark.django_db
def test_deal_payments():
    deal = DealFactory()
    PaymentFactory.create_batch(4, purpose=deal)

    assert deal.payments.count() == 4
