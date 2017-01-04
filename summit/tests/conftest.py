import pytest
from pytest_factoryboy import register

from account.factories import UserFactory
from summit.factories import SummitFactory, SummitLessonFactory, SummitAnketFactory

register(SummitFactory)
register(SummitAnketFactory)
register(SummitLessonFactory)
register(UserFactory)


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def summit(summit_factory):
    return summit_factory()
