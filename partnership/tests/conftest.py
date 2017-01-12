import pytest
from pytest_factoryboy import register

from account.factories import UserFactory
from partnership.factories import PartnerFactory, DealFactory
from payment.factories import PaymentFactory, PartnerPaymentFactory, DealPaymentFactory, CurrencyFactory

register(UserFactory)
register(PartnerFactory)
register(DealFactory)
register(PaymentFactory)
register(PartnerPaymentFactory)
register(DealPaymentFactory)
register(CurrencyFactory)


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def partner(partner_factory, user):
    return partner_factory(user=user)


@pytest.fixture
def deal(deal_factory, partner):
    return deal_factory(partnership=partner)


@pytest.fixture
def payment(payment_factory):
    return payment_factory()


@pytest.fixture
def currency(currency_factory):
    return currency_factory(name='Currency', short_name='cur.', symbol='c', code='cod')
