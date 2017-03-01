from datetime import date, datetime, timedelta

import pytest
from pytest_factoryboy import register

from account.factories import UserFactory
from account.models import CustomUser
from hierarchy.factories import HierarchyFactory, DepartmentFactory
from partnership.factories import PartnerFactory
from status.factories import DivisionFactory

register(UserFactory)
register(HierarchyFactory)
register(DepartmentFactory)
register(DivisionFactory)
register(PartnerFactory)


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
        return source.strftime('%Y-%m-%d %H:%M')
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
    return user_factory(username='testuser')


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
def user_data(partner):
    return {
        'email': 'test@email.com',
        'first_name': 'test_first',
        'last_name': 'test_last',
        'middle_name': 'test_middle',
        'search_name': 'test_search',
        'facebook': 'http://fb.com/test',
        'vkontakte': 'http://vk.com/test',
        'odnoklassniki': 'http://ok.com/test',
        'skype': 'test_skype',
        'phone_number': '1234567890',
        'extra_phone_numbers': ['1111', '2222', '3333'],
        'born_date': date(2000, 1, 1),
        'coming_date': date(2000, 2, 20),
        'repentance_date': date(2000, 2, 20),
        'country': 'Italy',
        'region': 'R',
        'city': 'C',
        'district': 'D',
        'address': 'A',
        'department': Factory('department_factory'),
        'spiritual_level': CustomUser.FATHER,
        'master': Factory('user_factory'),
        'hierarchy': Factory('hierarchy_factory'),
        'divisions': FactoryList('division_factory', 4),
        'partner': {
            'value': 100,
            'responsible': partner.id,
            'date': '2020-04-04',
        },
    }
