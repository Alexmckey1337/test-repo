import pytest
from decimal import Decimal

from datetime import date
from django.utils import six
from pytest_factoryboy import register
from rest_framework import status

from account.factories import UserFactory
from common.test_helpers.views import fake_dispatch
from hierarchy.factories import DepartmentFactory, HierarchyFactory
from partnership.factories import PartnerFactory, DealFactory, PartnerRoleFactory, PartnerGroupFactory
from partnership.models import Partnership, PartnerRole
from partnership.api.views import DealViewSet
from payment.factories import PaymentFactory, PartnerPaymentFactory, DealPaymentFactory, CurrencyFactory

register(UserFactory)
register(DepartmentFactory)
register(HierarchyFactory)
register(PartnerFactory)
register(PartnerGroupFactory)
register(PartnerRoleFactory)
register(DealFactory)
register(PaymentFactory)
register(PartnerPaymentFactory)
register(DealPaymentFactory)
register(CurrencyFactory)

#                                           is_responsible             is not responsible
CREATOR_PARTNERS = [
    {'user': 'user_user', 'code': (status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN)},
    {'user': 'user_manager', 'code': (status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN)},
    {'user': 'user_supervisor', 'code': (status.HTTP_201_CREATED, status.HTTP_201_CREATED)},
    {'user': 'user_director', 'code': (status.HTTP_201_CREATED, status.HTTP_201_CREATED)},
]

#                                           is_responsible             is not responsible
VIEWER_PARTNERS = [
    {'user': 'user_user', 'code': (status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN)},
    {'user': 'user_manager', 'code': (status.HTTP_200_OK, status.HTTP_403_FORBIDDEN)},
    {'user': 'user_supervisor', 'code': (status.HTTP_200_OK, status.HTTP_200_OK)},
    {'user': 'user_director', 'code': (status.HTTP_200_OK, status.HTTP_200_OK)},
]


class Factory:
    def __init__(self, factory_name):
        self.name = factory_name


FIELD_VALUE = list(six.iteritems({
    'responsible': (Factory('user_factory'),),
    'value': (Decimal(10), 40, Decimal(40)),
    'date': (date(2000, 2, 2), '2002-04-04', date(2002, 4, 4)),
    'need_text': ('old_text', 'new text'),
    'currency': (Factory('currency_factory'),),
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
def user_user(user_factory):
    return user_factory()


@pytest.fixture
def user_manager(partner_role_factory):
    return partner_role_factory(level=PartnerRole.MANAGER).user


@pytest.fixture
def user_supervisor(partner_role_factory):
    return partner_role_factory(level=PartnerRole.SUPERVISOR).user


@pytest.fixture
def user_director(partner_role_factory):
    return partner_role_factory(level=PartnerRole.DIRECTOR).user


@pytest.fixture(params=CREATOR_PARTNERS, ids=[cp['user'] for cp in CREATOR_PARTNERS])
def creator(request):
    return {'user': request.getfuncargvalue(request.param['user']), 'code': request.param['code']}


@pytest.fixture(params=VIEWER_PARTNERS, ids=[vp['user'] for vp in VIEWER_PARTNERS])
def viewer(request):
    return {'user': request.getfuncargvalue(request.param['user']), 'code': request.param['code']}


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
    if isinstance(r[1][0], Factory):
        old = request.getfuncargvalue(r[1][0].name)()
        new = request.getfuncargvalue(r[1][0].name)()
        return r[0], (old, new.id, new)
    return r[0], r[1]


@pytest.fixture
def api_login_supervisor_client(api_client, partner_role_factory):
    partner_role = partner_role_factory(level=PartnerRole.SUPERVISOR)
    api_client.force_login(user=partner_role.user)

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
