import pytest
from pytest_factoryboy import register

from account.factories import UserFactory
from notification.factories import NotificationThemeFactory, NotificationFactory

register(NotificationThemeFactory)
register(NotificationFactory)
register(UserFactory)


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def notification_theme(notification_theme_factory):
    return notification_theme_factory()


@pytest.fixture
def notification(notification_factory, user):
    return notification_factory(user=user)
