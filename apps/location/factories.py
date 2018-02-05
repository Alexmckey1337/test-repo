import factory
import factory.fuzzy

from . import models


class OldCountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OldCountry

    code = factory.Sequence(lambda n: n)
    title = factory.Sequence(lambda n: 'Country {}'.format(n))


class OldRegionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OldRegion

    code = factory.Sequence(lambda n: n)
    title = factory.Sequence(lambda n: 'Region {}'.format(n))
    country = factory.SubFactory(OldCountryFactory)


class OldCityFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OldCity

    code = factory.Sequence(lambda n: n)
    title = factory.Sequence(lambda n: 'City {}'.format(n))
    region = factory.SubFactory(OldRegionFactory)
    country = factory.SubFactory(OldCountryFactory)
