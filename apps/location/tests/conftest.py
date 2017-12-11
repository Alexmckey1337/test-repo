import pytest
from pytest_factoryboy import register

from apps.location.factories import CountryFactory, RegionFactory, CityFactory

register(CountryFactory)
register(RegionFactory)
register(CityFactory)


@pytest.fixture
def country(country_factory):
    return country_factory()


@pytest.fixture
def region(region_factory, country):
    return region_factory(country=country)


@pytest.fixture
def city(city_factory, country, region):
    return city_factory(country=country, region=region)
