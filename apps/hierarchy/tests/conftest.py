import pytest
from pytest_factoryboy import register

from apps.hierarchy.factories import DepartmentFactory, HierarchyFactory

register(DepartmentFactory)
register(HierarchyFactory)


@pytest.fixture
def department(department_factory):
    return department_factory()


@pytest.fixture
def hierarchy(hierarchy_factory):
    return hierarchy_factory()
