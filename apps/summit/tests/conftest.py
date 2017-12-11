import pytest
from pytest_factoryboy import register
from rest_framework import status

from apps.account.factories import UserFactory
from apps.hierarchy.factories import HierarchyFactory, DepartmentFactory
from apps.payment.factories import PaymentFactory, CurrencyFactory
from apps.summit.factories import (
    SummitFactory, SummitLessonFactory, SummitAnketFactory, SummitTypeFactory, AnketEmailFactory,
    SummitUserConsultantFactory, AnketNoteFactory, SummitAttendFactory, SummitTicketFactory, ProfileStatusFactory,
    VisitorLocationFactory)
from apps.summit.models import SummitAnket

register(SummitFactory)
register(SummitTypeFactory)
register(SummitAnketFactory)
register(SummitAttendFactory)
register(SummitTicketFactory)
register(VisitorLocationFactory)
register(ProfileStatusFactory)
register(SummitLessonFactory)
register(UserFactory)
register(PaymentFactory)
register(CurrencyFactory)
register(AnketEmailFactory)
register(SummitUserConsultantFactory)
register(AnketNoteFactory)
register(HierarchyFactory)
register(DepartmentFactory)


CREATOR_ANKET = [
    {'anket': 'anket_of_supervisor', 'code': status.HTTP_201_CREATED},
    {'anket': 'anket_of_consultant', 'code': status.HTTP_403_FORBIDDEN},
    {'anket': 'anket_of_visitor', 'code': status.HTTP_403_FORBIDDEN},
]

VIEWER_ANKET = [
    {'anket': 'anket_of_supervisor', 'code': status.HTTP_200_OK},
    {'anket': 'anket_of_consultant', 'code': status.HTTP_200_OK},
    {'anket': 'anket_of_visitor', 'code': status.HTTP_403_FORBIDDEN},
]


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
def ticket(summit_ticket_factory, summit):
    return summit_ticket_factory(summit=summit)


@pytest.fixture
def anket(summit_anket_factory, user, summit):
    return summit_anket_factory(user=user, summit=summit)


@pytest.fixture
def anket_of_visitor(summit_anket_factory, user_factory, summit):
    return summit_anket_factory(user=user_factory(), summit=summit, role=SummitAnket.VISITOR)


@pytest.fixture
def anket_of_consultant(summit_anket_factory, user_factory, summit):
    return summit_anket_factory(user=user_factory(), summit=summit, role=SummitAnket.CONSULTANT)


@pytest.fixture
def anket_of_supervisor(summit_anket_factory, user_factory, summit):
    return summit_anket_factory(user=user_factory(), summit=summit, role=SummitAnket.SUPERVISOR)


@pytest.fixture(params=CREATOR_ANKET, ids=[ca['anket'] for ca in CREATOR_ANKET])
def creator(request):
    return {'anket': request.getfuncargvalue(request.param['anket']), 'code': request.param['code']}


@pytest.fixture(params=VIEWER_ANKET, ids=[va['anket'] for va in VIEWER_ANKET])
def viewer(request):
    return {'anket': request.getfuncargvalue(request.param['anket']), 'code': request.param['code']}


@pytest.fixture
def anket_email(anket_email_factory, anket):
    return anket_email_factory(anket=anket)


@pytest.fixture
def lesson(summit_lesson_factory, summit):
    return summit_lesson_factory(summit=summit)


@pytest.fixture
def summit_uc(summit_user_consultant_factory, summit_anket_factory, summit, anket):
    return summit_user_consultant_factory(summit=summit, user=anket, consultant=summit_anket_factory())


@pytest.fixture
def department(department_factory):
    return department_factory()


@pytest.fixture
def hierarchy(hierarchy_factory):
    return hierarchy_factory()
