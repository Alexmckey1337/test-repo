import pytest
from pytest_django.lazy_django import skip_if_no_django
from pytest_factoryboy import register

from account.factories import UserFactory

register(UserFactory)


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture()
def api_client():
    skip_if_no_django()

    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture()
def api_login_client(api_client, user):
    api_client.force_login(user=user)

    return api_client
