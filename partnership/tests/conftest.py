import pytest
from pytest_factoryboy import register
from rest_framework import status

from account.factories import UserFactory
from partnership.factories import PartnerFactory, DealFactory
from partnership.models import Partnership
from payment.factories import PaymentFactory, PartnerPaymentFactory, DealPaymentFactory, CurrencyFactory

register(UserFactory)
register(PartnerFactory)
register(DealFactory)
register(PaymentFactory)
register(PartnerPaymentFactory)
register(DealPaymentFactory)
register(CurrencyFactory)

#                                           is_responsible             is not responsible
CREATOR_PARTNERS = [
    {'partner': 'partner_partner', 'code': (status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN)},
    {'partner': 'partner_manager', 'code': (status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN)},
    {'partner': 'partner_supervisor', 'code': (status.HTTP_201_CREATED, status.HTTP_201_CREATED)},
    {'partner': 'partner_director', 'code': (status.HTTP_201_CREATED, status.HTTP_201_CREATED)},
]

#                                           is_responsible             is not responsible
VIEWER_PARTNERS = [
    {'partner': 'partner_partner', 'code': (status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN)},
    {'partner': 'partner_manager', 'code': (status.HTTP_200_OK, status.HTTP_403_FORBIDDEN)},
    {'partner': 'partner_supervisor', 'code': (status.HTTP_200_OK, status.HTTP_200_OK)},
    {'partner': 'partner_director', 'code': (status.HTTP_200_OK, status.HTTP_200_OK)},
]


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


@pytest.fixture
def partner_partner(partner_factory, user_factory):
    return partner_factory(user=user_factory(), level=Partnership.PARTNER)


@pytest.fixture
def partner_manager(partner_factory, user_factory):
    return partner_factory(user=user_factory(), level=Partnership.MANAGER)


@pytest.fixture
def partner_supervisor(partner_factory, user_factory):
    return partner_factory(user=user_factory(), level=Partnership.SUPERVISOR)


@pytest.fixture
def partner_director(partner_factory, user_factory):
    return partner_factory(user=user_factory(), level=Partnership.DIRECTOR)


@pytest.fixture(params=CREATOR_PARTNERS, ids=[cp['partner'] for cp in CREATOR_PARTNERS])
def creator(request):
    return {'partner': request.getfuncargvalue(request.param['partner']), 'code': request.param['code']}


@pytest.fixture(params=VIEWER_PARTNERS, ids=[vp['partner'] for vp in VIEWER_PARTNERS])
def viewer(request):
    return {'partner': request.getfuncargvalue(request.param['partner']), 'code': request.param['code']}
