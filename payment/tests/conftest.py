import pytest
from pytest_factoryboy import register

from account.factories import UserFactory
from payment.factories import SummitAnketPaymentFactory, PartnerPaymentFactory, DealPaymentFactory, PaymentFactory, \
    CurrencyFactory
from partnership.factories import PartnerFactory, DealFactory
from summit.factories import SummitAnketFactory

register(UserFactory)
register(SummitAnketFactory)
register(PartnerFactory)
register(DealFactory)

register(PaymentFactory)
register(SummitAnketPaymentFactory)
register(PartnerPaymentFactory)
register(DealPaymentFactory)
register(CurrencyFactory)


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def anket(summit_anket_factory, user):
    return summit_anket_factory(user=user)


@pytest.fixture
def partner(partner_factory, user):
    return partner_factory(user=user)


@pytest.fixture
def deal(deal_factory, partner):
    return deal_factory(partnership=partner)


@pytest.fixture
def summit_anket_payment(summit_anket_payment_factory, anket):
    return summit_anket_payment_factory(purpose=anket)


@pytest.fixture
def partner_payment(partner_payment_factory, partner):
    return partner_payment_factory(purpose=partner)


@pytest.fixture
def deal_payment(deal_payment_factory, deal):
    return deal_payment_factory(purpose=deal)


@pytest.fixture
def payment(payment_factory):
    return payment_factory()


@pytest.fixture
def currency(currency_factory):
    return currency_factory(name='Currency', short_name='cur.', symbol='c', code='cod')
