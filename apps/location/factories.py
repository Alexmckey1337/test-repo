import factory
import factory.fuzzy

from . import models


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Country

    code = factory.Sequence(lambda n: n)
    title = factory.Sequence(lambda n: 'Country {}'.format(n))


class RegionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Region

    code = factory.Sequence(lambda n: n)
    title = factory.Sequence(lambda n: 'Region {}'.format(n))
    country = factory.SubFactory(CountryFactory)


class CityFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.City

    code = factory.Sequence(lambda n: n)
    title = factory.Sequence(lambda n: 'City {}'.format(n))
    region = factory.SubFactory(RegionFactory)
    country = factory.SubFactory(CountryFactory)
