import pytest
from django.db.models import signals

from pytest_factoryboy import register

from account.factories import UserFactory
from account.models import CustomUser, sync_user
from navigation.factories import TableFactory, NavigationFactory, CategoryFactory
from navigation.factories import UserColumnFactory, ColumnTypeFactory

register(UserFactory)
register(NavigationFactory)
register(CategoryFactory)
register(ColumnTypeFactory)
register(TableFactory)
register(UserColumnFactory)


@pytest.fixture(scope="module", autouse=True)
def disconnect_signals():
    signals.post_save.disconnect(sync_user, CustomUser)


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def navigation(navigation_factory):
    return navigation_factory()


@pytest.fixture
def category(category_factory):
    return category_factory()


@pytest.fixture
def column_type(column_type_factory, category):
    return column_type_factory(category=category)


@pytest.fixture
def table(table_factory, user):
    return table_factory(user=user)


@pytest.fixture
def user_column(user_column_factory, table, column_type):
    return user_column_factory(table=table, columnType=column_type)
