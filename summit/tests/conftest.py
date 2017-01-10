import pytest
from pytest_factoryboy import register

from account.factories import UserFactory
from payment.factories import PaymentFactory, CurrencyFactory
from summit.factories import (
    SummitFactory, SummitLessonFactory, SummitAnketFactory, SummitTypeFactory, AnketEmailFactory,
    SummitUserConsultantFactory, AnketNoteFactory)

register(SummitFactory)
register(SummitTypeFactory)
register(SummitAnketFactory)
register(SummitLessonFactory)
register(UserFactory)
register(PaymentFactory)
register(CurrencyFactory)
register(AnketEmailFactory)
register(SummitUserConsultantFactory)
register(AnketNoteFactory)


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def currency(currency_factory):
    return currency_factory()


@pytest.fixture
def summit_type(summit_type_factory):
    return summit_type_factory()


@pytest.fixture
def summit(summit_factory, summit_type, currency):
    return summit_factory(type=summit_type, currency=currency)


@pytest.fixture
def anket(summit_anket_factory, user, summit):
    return summit_anket_factory(user=user, summit=summit)


@pytest.fixture
def anket_email(anket_email_factory, anket):
    return anket_email_factory(anket=anket)


@pytest.fixture
def lesson(summit_lesson_factory, summit):
    return summit_lesson_factory(summit=summit)


@pytest.fixture
def summit_uc(summit_user_consultant_factory, summit_anket_factory, summit, anket):
    return summit_user_consultant_factory(summit=summit, user=anket, consultant=summit_anket_factory())
