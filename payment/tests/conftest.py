import pytest
from django.conf import settings
from pytest_factoryboy import register
from rest_framework import permissions

from account.factories import UserFactory
from partnership.factories import PartnerFactory, DealFactory, PartnerRoleFactory
from payment.factories import SummitAnketPaymentFactory, PartnerPaymentFactory, DealPaymentFactory, PaymentFactory, \
    CurrencyFactory
from payment.api.views import PaymentUpdateDestroyView, PaymentListView
from summit.factories import SummitAnketFactory
from summit.models import SummitAnket

register(UserFactory)
register(SummitAnketFactory)
register(PartnerFactory)
register(PartnerRoleFactory)
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
def visitor_anket(summit_anket_factory, user_factory):
    return summit_anket_factory(user=user_factory(), role=SummitAnket.VISITOR)


@pytest.fixture
def consultant_anket(summit_anket_factory, user_factory):
    return summit_anket_factory(user=user_factory(), role=SummitAnket.CONSULTANT)


@pytest.fixture
def supervisor_anket(summit_anket_factory, user_factory):
    return summit_anket_factory(user=user_factory(), role=SummitAnket.SUPERVISOR)


@pytest.fixture
def partner(partner_factory, user):
    return partner_factory(user=user)


@pytest.fixture
def partner_user(user_factory):
    return user_factory()


@pytest.fixture
def manager_user(partner_role_factory):
    return partner_role_factory(level=settings.PARTNER_LEVELS['manager']).user


@pytest.fixture
def supervisor_user(partner_role_factory):
    return partner_role_factory(level=settings.PARTNER_LEVELS['supervisor']).user


@pytest.fixture
def director_user(partner_role_factory):
    return partner_role_factory(level=settings.PARTNER_LEVELS['director']).user


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


@pytest.fixture(params=['deal_payment', 'partner_payment', 'summit_anket_payment'])
def purpose_payment(request):
    return request.getfuncargvalue(request.param)


@pytest.fixture(params=['deal_payment', 'partner_payment', 'summit_anket_payment'])
def have_permission_user(request):
    return request.getfuncargvalue(request.param)


@pytest.fixture(params=[
    'user',
    'partner_user', 'manager_user',
    'visitor_anket', 'consultant_anket', 'supervisor_anket'])
def dont_have_permission_user(request):
    return request.getfuncargvalue(request.param)


@pytest.fixture
def payment(payment_factory):
    return payment_factory()


@pytest.fixture
def currency(currency_factory):
    return currency_factory(name='Currency', short_name='cur.', symbol='c', code='cod')


@pytest.fixture
def allow_any_payment_update_destroy_view(monkeypatch):
    monkeypatch.setattr(PaymentUpdateDestroyView, 'permission_classes', (permissions.AllowAny,))

    return PaymentUpdateDestroyView


@pytest.fixture
def allow_any_payment_list_view(monkeypatch):
    monkeypatch.setattr(PaymentListView, 'permission_classes', (permissions.AllowAny,))

    return PaymentListView
