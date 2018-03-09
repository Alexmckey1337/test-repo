import datetime
from decimal import Decimal

import factory
import factory.fuzzy
import pytz

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
    created_at = factory.fuzzy.FuzzyDateTime(start_dt=datetime.datetime(2000, 1, 1, tzinfo=pytz.utc))
    manager = factory.SubFactory('apps.account.factories.UserFactory')

    currency_sum = factory.SubFactory(CurrencyFactory)
    rate = Decimal(1)


class SummitAnketPaymentFactory(PaymentFactory):
    purpose = factory.SubFactory('apps.summit.factories.SummitAnketFactory')


class PartnerPaymentFactory(PaymentFactory):
    purpose = factory.SubFactory('apps.partnership.factories.PartnerFactory')


class DealPaymentFactory(PaymentFactory):
    purpose = factory.SubFactory('apps.partnership.factories.DealFactory')
