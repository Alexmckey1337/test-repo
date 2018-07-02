from datetime import date, datetime, timedelta

import pytest
from pytest_factoryboy import register

from apps.account.factories import UserFactory
from apps.account.models import CustomUser
from apps.hierarchy.factories import HierarchyFactory, DepartmentFactory
from apps.partnership.factories import PartnerFactory, DealFactory, PartnerRoleFactory
from apps.payment.factories import CurrencyFactory
from apps.status.factories import DivisionFactory
from apps.summit.factories import SummitFactory, SummitTypeFactory, SummitAnketFactory

register(UserFactory)
register(CurrencyFactory)
register(HierarchyFactory)
register(DepartmentFactory)
register(DivisionFactory)
register(PartnerFactory)
register(PartnerRoleFactory)
register(DealFactory)
register(SummitFactory)
register(SummitTypeFactory)
register(SummitAnketFactory)
register(CurrencyFactory)


class Factory:
    def __init__(self, factory_name):
        self.name = factory_name


class FactoryList:
    def __init__(self, factory_name, count=2):
        self.name = factory_name
        self.count = count


def get_value(source, request=None):
    if isinstance(source, Factory):
        return request.getfuncargvalue(source.name)().id
    if isinstance(source, FactoryList):
        return [v.id for v in request.getfuncargvalue(source.name).create_batch(source.count)]
    if isinstance(source, date):
        return source.strftime('%Y-%m-%d')
    if isinstance(source, datetime):
        return source.strftime('%Y-%m-%d %H:%M:%S%z')
    return source


def get_values(data, request=None):
    for k in data:
        data[k] = get_value(data[k], request)
    return data


def change_field(value, source, request=None):
    if isinstance(source, (FactoryList, Factory)):
        return get_value(source, request)
    if isinstance(source, (date, datetime)):
        return get_value(source + timedelta(days=1), request)
    if isinstance(source, list):
        return value + ['1']
    if isinstance(source, (int, float)):
        return value + 1
    if isinstance(source, dict):
        return value
    return value + '1'


@pytest.fixture
def user(user_factory):
    return user_factory(username='testuser', hierarchy__level=0)


@pytest.fixture
def department(department_factory):
    return department_factory()


@pytest.fixture
def hierarchy(hierarchy_factory):
    return hierarchy_factory()


@pytest.fixture
def partner(partner_factory):
    return partner_factory()


@pytest.fixture
def staff_user(user_factory):
    return user_factory(username='staff', is_staff=True)


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
def user_data():
    return {
        'email': 'test@email.com',
        'first_name': 'test_first',
        'last_name': 'test_last',
        'middle_name': 'test_middle',
        'search_name': 'test_search',
        'language': 'en',
        'description': 'bla bla bla',
        'facebook': 'http://fb.com/test',
        'vkontakte': 'http://vk.com/test',
        'odnoklassniki': 'http://ok.com/test',
        'skype': 'test_skype',
        'phone_number': '1234567890',
        'extra_phone_numbers': ['1111222233', '2222333311', '3333111122'],
        'born_date': date(2000, 1, 1),
        'coming_date': date(2000, 2, 20),
        'repentance_date': date(2000, 2, 20),
        'country': 'Italy',
        'region': 'R',
        'city': 'C',
        'district': 'D',
        'address': 'A',
        'departments': FactoryList('department_factory', 1),
        'spiritual_level': CustomUser.FATHER,
        'master': Factory('user_factory'),
        'hierarchy': Factory('hierarchy_factory'),
        'divisions': FactoryList('division_factory', 4),
    }


@pytest.fixture
def divisions(division_factory):
    return division_factory.create_batch(2)
