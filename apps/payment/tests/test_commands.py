# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from decimal import Decimal
from django.core import management
import pytest

from apps.payment.models import Payment


@pytest.mark.django_db
class TestUpdatePaymentEffectiveSum:
    def test_command(self, payment_factory):
        first_payment = payment_factory(sum=Decimal(10), rate=Decimal(2))
        second_payment = payment_factory(sum=Decimal(20), rate=Decimal(4))

        first_payment.effective_sum = 40
        second_payment.effective_sum = 10
        first_payment.save(update_eff_sum=False)
        second_payment.save(update_eff_sum=False)

        assert Payment.objects.get(id=first_payment.id).effective_sum == Decimal(40)
        assert Payment.objects.get(id=second_payment.id).effective_sum == Decimal(10)

        management.call_command('update_payment_effective_sum')

        assert Payment.objects.get(id=first_payment.id).effective_sum == Decimal(20)
        assert Payment.objects.get(id=second_payment.id).effective_sum == Decimal(80)
