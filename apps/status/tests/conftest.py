import pytest
from pytest_factoryboy import register

from apps.status.factories import StatusFactory, DivisionFactory

register(StatusFactory)
register(DivisionFactory)


@pytest.fixture
def division(division_factory):
    return division_factory()


@pytest.fixture
def status(status_factory):
    return status_factory()
