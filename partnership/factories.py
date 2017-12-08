import datetime
from decimal import Decimal

import factory
import factory.fuzzy

from . import models


class PartnerFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Partnership

    user = factory.SubFactory('account.factories.UserFactory')
    value = Decimal(400)
    date = factory.fuzzy.FuzzyDate(start_date=datetime.date(2000, 1, 1))


class DealFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Deal

    value = Decimal(100)
    partnership = factory.SubFactory(PartnerFactory)

    date_created = factory.fuzzy.FuzzyDate(start_date=datetime.date(2002, 1, 1))
    date = factory.LazyAttribute(lambda o: o.date_created + datetime.timedelta(o.duration))

    class Params:
        duration = 6


class PartnerRoleFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PartnerRole

    user = factory.SubFactory('account.factories.UserFactory')
    level = models.PartnerRole.MANAGER


class PartnerGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PartnerGroup

    title = factory.Sequence(lambda n: 'title{}'.format(n))
