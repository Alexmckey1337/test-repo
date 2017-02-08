import pytest
from pytest_factoryboy import register
from rest_framework import serializers

from common.fields import DecimalWithCurrencyField
from payment.factories import CurrencyFactory

register(CurrencyFactory)


@pytest.fixture
def currency(currency_factory):
    return currency_factory(name='Currency', short_name='cur.', symbol='c', code='cod')


class MockDecimalField:
    def __init__(self, *args, **kwargs):
        pass

    def get_attribute(self, instance):
        return 120

    def to_representation(self, value):
        return value


@pytest.fixture
def decimal_with_currency_field(monkeypatch):
    monkeypatch.setattr(serializers, 'DecimalField', MockDecimalField)
    DecimalWithCurrencyField.__bases__ = (serializers.DecimalField,)
    # monkeypatch.setattr(DecimalWithCurrencyField, '__bases__', (MockDecimalField,))

    return DecimalWithCurrencyField
