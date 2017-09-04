import pytest
from decimal import Decimal

from django.utils import six
from pytest_factoryboy import register
from rest_framework import status

from account.factories import UserFactory
from common.test_helpers.views import fake_dispatch
from hierarchy.factories import DepartmentFactory, HierarchyFactory
from partnership.factories import PartnerFactory, DealFactory
from partnership.models import Partnership
from partnership.views import DealViewSet
from payment.factories import PaymentFactory, PartnerPaymentFactory, DealPaymentFactory, CurrencyFactory

register(UserFactory)
register(DepartmentFactory)
register(HierarchyFactory)
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


FIELD_VALUE = list(six.iteritems({
    'value': (Decimal(10), 40, Decimal(40)),
    'need_text': ('old_text', 'new text'),
    'is_active': (True, 'false', False),
}))


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


@pytest.fixture
def values(currency_factory, partner_factory):
    old_currency, new_currency = currency_factory(), currency_factory()
    old_partner, new_partner = partner_factory(), partner_factory()
    fields = {
        'value': (Decimal(10), 40, Decimal(40)),
        'currency': (old_currency, new_currency.id, new_currency),
        'need_text': ('old_text', 'new text'),
        'is_active': (True, 'false', False),
        'level': (Partnership.PARTNER, Partnership.MANAGER),
        'responsible': (new_partner, old_partner.id, old_partner)
    }
    return six.iteritems(fields)


@pytest.fixture(params=FIELD_VALUE, ids=[f[0] for f in FIELD_VALUE])
def field_value(request):
    r = request.param
    return r[0], r[1]


@pytest.fixture
def api_login_supervisor_client(api_client, partner_factory):
    partner = partner_factory(level=Partnership.SUPERVISOR)
    api_client.force_login(user=partner.user)

    return api_client


@pytest.fixture
def partner_with_deals(partner, deal_factory):
    deal_factory.create_batch(2, partnership=partner, done=True, expired=False)
    deal_factory.create_batch(4, partnership=partner, done=False, expired=False)
    deal_factory.create_batch(8, partnership=partner, done=False, expired=True)

    return partner


@pytest.fixture
def fake_deal_view_set(monkeypatch):
    monkeypatch.setattr(DealViewSet, 'dispatch', fake_dispatch)

    return DealViewSet
