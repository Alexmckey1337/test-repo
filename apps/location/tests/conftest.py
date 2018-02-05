import pytest
from pytest_factoryboy import register

from apps.location.factories import OldCountryFactory, OldRegionFactory, OldCityFactory

register(OldCountryFactory)
register(OldRegionFactory)
register(OldCityFactory)


@pytest.fixture
def country(old_country_factory):
    return old_country_factory()


@pytest.fixture
def region(old_region_factory, country):
    return old_region_factory(country=country)


@pytest.fixture
def city(old_city_factory, country, region):
    return old_city_factory(country=country, region=region)
