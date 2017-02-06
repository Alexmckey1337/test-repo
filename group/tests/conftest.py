import pytest

from pytest_factoryboy import register

from account.factories import UserFactory
from group.factories import ChurchFactory
from group.factories import HomeGroupFactory
from hierarchy.factories import DepartmentFactory, HierarchyFactory

register(UserFactory)
register(ChurchFactory)
register(HomeGroupFactory)
register(DepartmentFactory)
register(HierarchyFactory)


@pytest.fixture
def pastor_hierarchy(hierarchy_factory):
    return hierarchy_factory(level=2)


@pytest.fixture
def leader_hierarchy(hierarchy_factory):
    return hierarchy_factory(level=1)


@pytest.fixture
def department(department_factory):
    return department_factory()


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def pastor(user_factory, pastor_hierarchy):
    return user_factory(hierarchy=pastor_hierarchy)


@pytest.fixture
def leader(user_factory, leader_hierarchy):
    return user_factory(hierarchy=leader_hierarchy)


@pytest.fixture
def church(church_factory, pastor, department):
    return church_factory(pastor=pastor, department=department)


@pytest.fixture
def home_group(home_group_factory, church, leader):
    return home_group_factory(church=church, leader=leader)
