import factory.fuzzy

from . import models


class MaxCodeError(Exception):
    pass


def country_codes(n):
    if not (0 <= n < 27 * 26):
        raise MaxCodeError('code must be between 0 and 26*27')
    first_symbol = '' if n < 26 else chr(n // 26 + 64)
    second_symbol = chr(n % 26 + 65)

    return f'{first_symbol}{second_symbol}'


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


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Country

    id = factory.Sequence(country_codes)
    name = factory.Sequence(lambda n: 'Country {}'.format(n))


class AreaFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Area

    name = factory.Sequence(lambda n: 'Area{}'.format(n))
    country = factory.SubFactory(CountryFactory)


class CityFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.City

    name = factory.Sequence(lambda n: 'Area{}'.format(n))
    area = factory.SubFactory(AreaFactory)
    country = factory.SubFactory(CountryFactory)
