import datetime

import factory
import factory.fuzzy

from . import models


CITIES = ['Tokyo', 'Lisbon', 'Paris', 'Melbourne', 'Santiago']
COUNTRIES = ['Ukraine', 'Chine', 'Russia', 'Italy', 'India', 'Ghana']


class ChurchFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Church

    department = factory.SubFactory('hierarchy.factories.DepartmentFactory')
    pastor = factory.SubFactory('account.factories.UserFactory')
    country = factory.Iterator(COUNTRIES)
    is_open = True

    opening_date = factory.fuzzy.FuzzyDate(start_date=datetime.date(2002, 1, 1))
    title = factory.Sequence(lambda n: 'Church #{}'.format(n))
    city = factory.Iterator(CITIES)
    address = '221B Baker Street'


class HomeGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.HomeGroup

    church = factory.SubFactory(ChurchFactory)
    leader = factory.SubFactory('account.factories.UserFactory')

    opening_date = factory.fuzzy.FuzzyDate(start_date=datetime.date(2002, 1, 1))
    title = factory.Sequence(lambda n: 'Home Group #{}'.format(n))
    city = factory.Iterator(CITIES)

    address = '221B Baker Street'
