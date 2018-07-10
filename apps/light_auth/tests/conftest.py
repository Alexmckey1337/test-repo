import pytest
from pytest_factoryboy import register

from apps.account.factories import UserFactory
from apps.light_auth.factories import LightAuthUserFactory, PhoneNumberFactory, PhoneConfirmationFactory


register(UserFactory)
register(LightAuthUserFactory)
register(PhoneNumberFactory)
register(PhoneConfirmationFactory)


@pytest.fixture
def light_user(light_auth_user_factory):
    return light_auth_user_factory()
