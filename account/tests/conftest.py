import pytest
from pytest_factoryboy import register

from account.factories import UserFactory
from hierarchy.factories import HierarchyFactory, DepartmentFactory

register(UserFactory)
register(HierarchyFactory)
register(DepartmentFactory)


@pytest.fixture
def user(user_factory):
    return user_factory(username='testuser')
