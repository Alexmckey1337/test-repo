# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from collections import namedtuple

import pytest
from django.contrib.auth.models import User
from rest_framework.permissions import SAFE_METHODS

from account.models import CustomUser
from partnership.models import Deal, Partnership
from payment.permissions import PaymentPermission, PaymentManager, PaymentManagerOrSupervisor
from summit.models import SummitAnket
from summit.permissions import IsConsultantReadOnly, IsSupervisorOrHigh as IsSummitSupervisorOrHigh

Qs = namedtuple('Qs', ['model'])


def blank_args(n):
    return (None for _ in range(n))


@pytest.mark.django_db
class TestPaymentPermission:
    @pytest.mark.parametrize('is_supervisor', [lambda self, a, b, c: True, lambda self, a, b, c: False],
                             ids=['supervisor', 'non supervisor'])
    @pytest.mark.parametrize('is_consultant', [lambda self, a, b, c: True, lambda self, a, b, c: False],
                             ids=['consultant', 'non consultant'])
    def test_has_object_permission_for_anket(self, monkeypatch, is_supervisor, is_consultant):
        monkeypatch.setattr(IsConsultantReadOnly, 'has_object_permission', is_consultant)
        monkeypatch.setattr(IsSummitSupervisorOrHigh, 'has_object_permission', is_supervisor)
        view = type('View', (), {'get_queryset': lambda: Qs(SummitAnket)})

        assert (PaymentPermission().has_object_permission(None, view, None) ==
                any((is_supervisor(*blank_args(4)), is_consultant(*blank_args(4)))))

    @pytest.mark.parametrize('view', [type('View', (), {'get_queryset': lambda: Qs(Deal)}),
                                      type('View', (), {'get_queryset': lambda: Qs(Partnership)})],
                             ids=['deal', 'partner'])
    @pytest.mark.parametrize(
        'is_supervisor,has_perm', [(property(lambda s: True), True), (property(lambda s: False), False)],
        ids=['supervisor', 'non supervisor'])
    @pytest.mark.parametrize('is_disciples', [lambda self, a: True, lambda self, a: False],
                             ids=['disciples', 'non disciples'])
    @pytest.mark.parametrize('is_manager', [lambda self: True, lambda self: False],
                             ids=['manager', 'non manager'])
    @pytest.mark.parametrize('method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
    def test_has_object_permission_for_partner_or_deal(
            self, user, monkeypatch, is_manager, is_disciples, is_supervisor, has_perm, view, method):
        monkeypatch.setattr(CustomUser, 'is_partner_manager_or_high', property(is_manager))
        monkeypatch.setattr(CustomUser, 'is_partner_responsible_of', is_disciples)
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', is_supervisor)
        request = type('Request', (), {'user': user, 'method': method})
        partner = type('Purpose', (), {'user': None})
        purpose = type('Purpose', (), {'user': None, 'partnership': partner})

        assert (PaymentPermission().has_object_permission(request, view, purpose) ==
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
        'is_supervisor,has_perm', [(lambda self, a, b, c: True, True), (lambda self, a, b, c: False, False)],
        ids=['supervisor', 'non supervisor'])
    def test_has_object_permission_for_anket(self, monkeypatch, user, summit_anket_payment, is_supervisor, has_perm):
        monkeypatch.setattr(PaymentManager, 'has_object_permission', lambda *args: False)
        monkeypatch.setattr(IsSummitSupervisorOrHigh, 'has_object_permission', is_supervisor)
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
