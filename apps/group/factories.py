import datetime

import factory
import factory.fuzzy

from . import models


CITIES = ['Tokyo', 'Lisbon', 'Paris', 'Melbourne', 'Santiago']
COUNTRIES = ['Ukraine', 'Chine', 'Russia', 'Italy', 'India', 'Ghana']


class DirectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Direction

    code = factory.Sequence(lambda n: f'code_{n:0>4d}')
    title_ru = factory.Sequence(lambda n: f'title_ru_{n:0>4d}')
    title_en = factory.Sequence(lambda n: f'title_en_{n:0>4d}')
    title_de = factory.Sequence(lambda n: f'title_de_{n:0>4d}')


class ChurchFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Church

    department = factory.SubFactory('apps.hierarchy.factories.DepartmentFactory')
    pastor = factory.SubFactory('apps.account.factories.UserFactory')
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
    leader = factory.SubFactory('apps.account.factories.UserFactory')

    opening_date = factory.fuzzy.FuzzyDate(start_date=datetime.date(2002, 1, 1))
    title = factory.Sequence(lambda n: 'Home Group #{}'.format(n))
    city = factory.Iterator(CITIES)

    address = '221B Baker Street'
