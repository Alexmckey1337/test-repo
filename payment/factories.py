import datetime
from decimal import Decimal

import factory
import factory.fuzzy
from . import models


class CurrencyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Currency

    name = factory.Sequence(lambda n: 'Currency #{}'.format(n))
    short_name = factory.Sequence(lambda n: 'cur{}'.format(n))
    code = factory.Sequence(lambda n: 'code_{}'.format(n))
    symbol = factory.Sequence(lambda n: 'c{}'.format(n))
    output_format = '{value} {short_name}'


class PaymentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Payment

    sum = Decimal(200)
    created_at = factory.fuzzy.FuzzyDate(start_date=datetime.date(2000, 1, 1))
    manager = factory.SubFactory('account.factories.UserFactory')

    currency_sum = factory.SubFactory(CurrencyFactory)
    rate = Decimal(1)


class SummitAnketPaymentFactory(PaymentFactory):
    purpose = factory.SubFactory('summit.factories.SummitAnketFactory')


class PartnerPaymentFactory(PaymentFactory):
    purpose = factory.SubFactory('partnership.factories.PartnerFactory')


class DealPaymentFactory(PaymentFactory):
    purpose = factory.SubFactory('partnership.factories.DealFactory')