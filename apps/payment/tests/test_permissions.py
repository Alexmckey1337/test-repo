from collections import namedtuple

import pytest
from django.contrib.auth.models import User
from rest_framework.permissions import SAFE_METHODS

from apps.account.models import CustomUser
from apps.partnership.models import Deal, ChurchDeal
from apps.payment.api.permissions import PaymentPermission, PaymentManager, PaymentManagerOrSupervisor
from apps.summit.models import SummitAnket

Qs = namedtuple('Qs', ['model'])


def blank_args(n):
    return (None for _ in range(n))


@pytest.mark.django_db
class TestPaymentPermission:
    @pytest.mark.parametrize('is_supervisor', [lambda self, a: True, lambda self, a: False],
                             ids=['supervisor', 'non supervisor'])
    @pytest.mark.parametrize('is_consultant', [lambda self, a: True, lambda self, a: False],
                             ids=['consultant', 'non consultant'])
    @pytest.mark.parametrize('method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
    def test_has_object_permission_for_anket(self, monkeypatch, user, is_supervisor, is_consultant, method):
        monkeypatch.setattr(CustomUser, 'is_summit_consultant_or_high', is_consultant)
        monkeypatch.setattr(CustomUser, 'is_summit_supervisor_or_high', is_supervisor)
        view = type('View', (), {'get_queryset': lambda: Qs(SummitAnket)})
        request = type('Request', (), {'user': user, 'method': method})

        assert (PaymentPermission().has_object_permission(request, view, None) ==
                any((is_supervisor(*blank_args(2)), (is_consultant(*blank_args(2)) and method in SAFE_METHODS))))

    @pytest.mark.parametrize(
        'is_supervisor,has_perm', [(property(lambda s: True), True), (property(lambda s: False), False)],
        ids=['supervisor', 'non supervisor'])
    @pytest.mark.parametrize('is_disciples', [lambda self, a: True, lambda self, a: False],
                             ids=['disciples', 'non disciples'])
    @pytest.mark.parametrize('is_manager', [lambda self: True, lambda self: False],
                             ids=['manager', 'non manager'])
    @pytest.mark.parametrize('method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
    def test_has_object_permission_for_deal(
            self, user, monkeypatch, is_manager, is_disciples, is_supervisor, has_perm, method):
        monkeypatch.setattr(CustomUser, 'is_partner_manager_or_high', property(is_manager))
        monkeypatch.setattr(CustomUser, 'is_partner_responsible_of', is_disciples)
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', is_supervisor)
        request = type('Request', (), {'user': user, 'method': method})
        partner = type('Purpose', (), {'user': None})
        purpose = type('Purpose', (), {'user': None, 'partnership': partner})

        assert (PaymentPermission().has_object_permission(
            request, type('View', (), {'get_queryset': lambda: Qs(Deal)}), purpose) ==
                has_perm or (is_disciples(*blank_args(2)) and method in SAFE_METHODS and is_manager(*blank_args(1))))

    @pytest.mark.parametrize(
        'is_supervisor,has_perm', [(property(lambda s: True), True), (property(lambda s: False), False)],
        ids=['supervisor', 'non supervisor'])
    @pytest.mark.parametrize('is_disciples', [lambda self, a: True, lambda self, a: False],
                             ids=['disciples', 'non disciples'])
    @pytest.mark.parametrize('is_manager', [lambda self: True, lambda self: False],
                             ids=['manager', 'non manager'])
    @pytest.mark.parametrize('method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
    def test_has_object_permission_for_church_deal(
            self, user, monkeypatch, is_manager, is_disciples, is_supervisor, has_perm, method):
        monkeypatch.setattr(CustomUser, 'is_partner_manager_or_high', property(is_manager))
        monkeypatch.setattr(CustomUser, 'is_partner_responsible_of_church', is_disciples)
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', is_supervisor)
        request = type('Request', (), {'user': user, 'method': method})
        partner = type('Purpose', (), {'church': None})
        purpose = type('Purpose', (), {'church': None, 'partnership': partner})

        assert (PaymentPermission().has_object_permission(
            request, type('View', (), {'get_queryset': lambda: Qs(ChurchDeal)}), purpose) ==
                has_perm or (is_disciples(*blank_args(2)) and method in SAFE_METHODS and is_manager(*blank_args(1))))

    def test_has_object_permission_for_other(self):
        view = type('View', (), {'get_queryset': lambda: Qs(User)})
        assert not PaymentPermission().has_object_permission(None, view, None)


@pytest.mark.django_db
class TestPaymentManager:
    def test_has_object_permission_is_manager(self, user, payment_factory):
        payment = payment_factory(manager=user)
        request = type('Request', (), {'user': user})
        assert PaymentManager().has_object_permission(request, None, payment)

    def test_has_object_permission_non_manager(self, user, payment):
        request = type('Request', (), {'user': user})
        assert not PaymentManager().has_object_permission(request, None, payment)


@pytest.mark.django_db
class TestPaymentManagerOrSupervisor:
    def test_has_object_permission_for_manager(self, monkeypatch, user, payment):
        monkeypatch.setattr(PaymentManager, 'has_object_permission', lambda *args: True)
        request = type('Request', (), {'user': user})

        assert PaymentManagerOrSupervisor().has_object_permission(request, None, payment)

    @pytest.mark.parametrize(
        'is_supervisor,has_perm', [(lambda self, a: True, True), (lambda self, a: False, False)],
        ids=['supervisor', 'non supervisor'])
    def test_has_object_permission_for_anket(self, monkeypatch, user, summit_anket_payment, is_supervisor, has_perm):
        monkeypatch.setattr(PaymentManager, 'has_object_permission', lambda *args: False)
        monkeypatch.setattr(CustomUser, 'is_summit_supervisor_or_high', is_supervisor)
        request = type('Request', (), {'user': user})

        assert PaymentManagerOrSupervisor().has_object_permission(request, None, summit_anket_payment) == has_perm

    @pytest.mark.parametrize(
        'is_supervisor,has_perm', [(property(lambda s: True), True), (property(lambda s: False), False)],
        ids=['supervisor', 'non supervisor'])
    def test_has_object_permission_for_partner(self, monkeypatch, user, partner_payment, is_supervisor, has_perm):
        monkeypatch.setattr(PaymentManager, 'has_object_permission', lambda *args: False)
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', is_supervisor)
        request = type('Request', (), {'user': user})

        assert PaymentManagerOrSupervisor().has_object_permission(request, None, partner_payment) == has_perm

    @pytest.mark.parametrize(
        'is_supervisor,has_perm', [(property(lambda s: True), True), (property(lambda s: False), False)],
        ids=['supervisor', 'non supervisor'])
    def test_has_object_permission_for_deal(self, monkeypatch, user, deal_payment, is_supervisor, has_perm):
        monkeypatch.setattr(PaymentManager, 'has_object_permission', lambda *args: False)
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', is_supervisor)
        request = type('Request', (), {'user': user})

        assert PaymentManagerOrSupervisor().has_object_permission(request, None, deal_payment) == has_perm

    def test_has_object_permission_for_other(self, monkeypatch, user, payment):
        monkeypatch.setattr(PaymentManager, 'has_object_permission', lambda *args: False)
        request = type('Request', (), {'user': user})

        assert not PaymentManagerOrSupervisor().has_object_permission(request, None, payment)
