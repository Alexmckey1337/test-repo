import pytest
from pytest_factoryboy import register

from account.factories import UserFactory
from hierarchy.factories import HierarchyFactory, DepartmentFactory
from partnership.factories import PartnerFactory
from status.factories import DivisionFactory

register(UserFactory)
register(HierarchyFactory)
register(DepartmentFactory)
register(DivisionFactory)
register(PartnerFactory)


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
def user_data(department, user, hierarchy, partner, division_factory):
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
            'additional_phones': '24681357',
            'born_date': '2000-01-01',
            'coming_date': '2000-02-20',
            'repentance_date': '2000-02-20',
            'country': 'Italy',
            'region': 'R',
            'city': 'C',
            'district': 'D',
            'address': 'A',
            'department': department.id,
            'master': user.id,
            'hierarchy': hierarchy.id,
            'divisions': [d.id for d in division_factory.create_batch(4)],
            'partner': {
                'value': 100,
                'responsible': partner.id,
                'date': '2020-04-04',
            },
        }