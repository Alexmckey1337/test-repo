import copy
import datetime
import itertools

import pytest
import pytz
from django.conf import settings
from django.urls import reverse
from rest_framework import status

from apps.account.models import CustomUser
from apps.account.tests.conftest import get_values, change_field
from apps.hierarchy.models import Hierarchy

FIELD_CODES = (
    # optional fields
    ('email', 201),
    ('search_name', 201),
    ('description', 201),
    ('facebook', 201),
    ('vkontakte', 201),
    ('odnoklassniki', 201),
    ('skype', 201),
    ('extra_phone_numbers', 201),
    ('born_date', 201),
    ('coming_date', 201),
    ('repentance_date', 201),
    ('country', 201),
    ('region', 201),
    ('city', 201),
    ('district', 201),
    ('address', 201),
    ('divisions', 201),
    ('spiritual_level', 201),

    # required fields
    ('first_name', 400),
    ('last_name', 400),
    ('middle_name', 400),
    ('phone_number', 400),
    ('departments', 400),
    ('hierarchy', 400),
    ('language', 400),
)

CHANGE_FIELD = (
    # non unique
    ('email', 400),
    ('search_name', 400),
    ('description', 400),
    ('facebook', 400),
    ('vkontakte', 400),
    ('odnoklassniki', 400),
    ('skype', 400),
    ('extra_phone_numbers', 400),
    ('born_date', 400),
    ('coming_date', 400),
    ('repentance_date', 400),
    ('country', 400),
    ('region', 400),
    ('city', 400),
    ('district', 400),
    ('address', 400),
    ('divisions', 400),
    ('spiritual_level', 400),
    ('departments', 400),
    ('master', 400),
    ('hierarchy', 400),
    ('language', 400),

    # unique
    ('first_name', 201),
    ('last_name', 201),
    ('middle_name', 201),
    ('phone_number', 201),
)

ALL_HIERARCHIES = [0, 1, 2, 4, 60, 70, 80]
HIERARCHY_LEVELS_UP = list(itertools.combinations_with_replacement(ALL_HIERARCHIES, 2))
HIERARCHY_LEVELS_DOWN = list(itertools.combinations(reversed(ALL_HIERARCHIES), 2))


def strptime(d):
    return pytz.utc.localize(datetime.datetime.strptime(d, '%Y-%m-%d'))


def get_hierarchies_down_correct():
    for h in HIERARCHY_LEVELS_DOWN:
        for l in settings.CHANGE_HIERARCHY_LEVELS[h[1]]:
            yield (h[0], h[1], l)


def get_hierarchies_down_incorrect():
    for h in HIERARCHY_LEVELS_DOWN:
        for l in (set(ALL_HIERARCHIES) - settings.CHANGE_HIERARCHY_LEVELS[h[1]]):
            yield (h[0], h[1], l)


@pytest.mark.django_db
class TestUserViewSet:
    def test_partial_update_main_info(self, user, api_login_client, user_factory):
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'first_name': 'test_first',
            'last_name': 'test_last',
            'middle_name': 'test_middle',
            'born_date': '2000-01-01',
            'country': 'Italy',
            'region': 'R',
            'city': 'C',
            'district': 'D',
            'address': 'A'
        }
        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

        user_dict = dict(list(CustomUser.objects.filter(username='testuser').values(*data.keys()))[0])
        data['born_date'] = datetime.date(*map(lambda d: int(d), data['born_date'].split('-')))

        assert user_dict == data

    def test_partial_update_contact_info(self, user, api_login_client, user_factory):
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'language': 'en',
            'phone_number': '+380886664422',
            'extra_phone_numbers': ['+380776664422'],
            'email': 'test@email.com',
            'skype': 'skype',
            'facebook': 'http://fb.com/test',
            'vkontakte': 'http://vk.com/test',
            'odnoklassniki': 'http://ok.com/test',
        }
        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

        user_dict = dict(list(CustomUser.objects.filter(username='testuser').values(*data.keys()))[0])

        assert user_dict == data

    def test_partial_update_master_hierarchy_department(self, user, api_login_client, user_factory,
                                                        hierarchy_factory, department_factory):
        master = user_factory(username='master')
        hierarchy = hierarchy_factory()
        department = department_factory()

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'master': master.id,
            'hierarchy': hierarchy.id,
            'departments': [department.id],
        }
        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

        departments = data.pop('departments')
        user_dict = dict(list(CustomUser.objects.filter(username='testuser').values(*data.keys()))[0])

        assert user_dict == data
        assert departments == list(user.departments.values_list('id', flat=True))

    def test_user_list_filter_by_hierarchy(self, api_login_client, user_factory, hierarchy_factory):
        other_hierarchy = hierarchy_factory()
        hierarchy = hierarchy_factory()
        user_factory.create_batch(10, hierarchy=hierarchy)
        user_factory.create_batch(20, hierarchy=other_hierarchy)

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?hierarchy={}'.format(url, hierarchy.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_department(self, api_login_client, user_factory, department_factory):
        other_department = department_factory()
        department = department_factory()
        users = user_factory.create_batch(10)
        for u in users:
            u.departments.set([department])
        users = user_factory.create_batch(20)
        for u in users:
            u.departments.set([other_department])

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?department={}'.format(url, department.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_master(self, api_login_client, user_factory):
        master = user_factory(username='master')
        # user_factory.create_batch(10, master=master)
        for i in range(10):
            master.add_child(username='user{}'.format(i), master=master)
        user_factory.create_batch(20)

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?master={}'.format(url, master.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_multi_master(self, api_login_client, user_factory):
        master = user_factory(username='master')
        other_master = user_factory(username='other_master')
        # user_factory.create_batch(10, master=master)
        for i in range(10):
            master.add_child(username='master{}'.format(i), master=master)
        # user_factory.create_batch(40, master=other_master)
        for i in range(40):
            other_master.add_child(username='other_master{}'.format(i), master=other_master)
        user_factory.create_batch(20)

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?master={}&master={}'.format(url, master.id, other_master.id),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 50

    def test_user_list_filter_by_master_tree(self, api_login_client, user_factory):
        user = user_factory()  # count: + 0, = 0, all_users_count: +1, = 1

        # user_factory.create_batch(3, master=user)  # count: + 3, = 3, all_users_count: +3, = 4
        for i in range(3):
            user.add_child(username='user{}'.format(i), master=user)
        # second_level_user = user_factory(master=user)  # count: + 1, = 4, all_users_count: +1, = 5
        second_level_user = user.add_child(username='second_level_user', master=user)
        # user_factory.create_batch(8, master=second_level_user)  # count: + 8, = 12, all_users_count: +8, = 13
        for i in range(8):
            second_level_user.add_child(username='second_level_user{}'.format(i), master=second_level_user)

        user_factory.create_batch(15)  # count: + 0, = 12, all_users_count: +15, = 28
        other_user = user_factory()  # count: + 0, = 12, all_users_count: +1, = 29
        # user_factory.create_batch(32, master=other_user)  # count: + 0, = 12, all_users_count: + 32, = 61
        for i in range(32):
            other_user.add_child(username='other_user{}'.format(i), master=other_user)

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(url, data={'master_tree': user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 13

    def test_user_search_by_fio(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        user_factory(last_name='searchlast', first_name='searchfirst')

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_fio={}'.format(url, 'searchfirst searchlast'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_user_search_by_email(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        user_factory(email='mysupermail@test.com')
        user_factory(email='test@mysupermail.com')

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_email={}'.format(url, 'mysupermail'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_phone(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        user_factory(phone_number='+380990002246')
        user_factory(phone_number='+380992299000')

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_phone_number={}'.format(url, '99000'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_country(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        user_factory.create_batch(8, country='Ukraine')

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_country={}'.format(url, 'Ukraine'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_user_search_by_city(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        user_factory.create_batch(8, city='Tokio')

        url = reverse('tables-user')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_city={}'.format(url, 'Tokio'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_current_user_as_pk(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        current_user = user_factory(is_staff=True)

        url = reverse('users_v1_1-detail', kwargs={'pk': 'current'})

        api_login_client.force_login(user=current_user)
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == current_user.id

    def test_get_queryset_as_staff_current_user(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        current_user = user_factory(is_staff=True)

        url = reverse('tables-user')

        api_login_client.force_login(user=current_user)
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 12

    def test_get_queryset_as_current_user_without_hierarchy(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        current_user = user_factory(hierarchy=None)

        url = reverse('tables-user')

        api_login_client.force_login(user=current_user)
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_queryset_as_current_user_with_hierarchy_less_then_2(self, api_client, user_factory,
                                                                     hierarchy_factory):
        hierarchy = hierarchy_factory(level=1)
        current_user = user_factory(hierarchy=hierarchy)
        # first_level = user_factory(hierarchy=hierarchy, master=current_user)
        first_level = current_user.add_child(hierarchy=hierarchy, username='current_user_child', master=current_user)
        # second_level = user_factory(hierarchy=hierarchy, master=first_level)
        second_level = first_level.add_child(hierarchy=hierarchy, username='first_level_child', master=first_level)
        # user_factory(hierarchy=hierarchy, master=current_user)
        current_user.add_child(hierarchy=hierarchy, username='current_user_other', master=current_user)
        # user_factory.create_batch(8, hierarchy=hierarchy, master=first_level)
        for i in range(8):
            first_level.add_child(hierarchy=hierarchy, username='first_level{}'.format(i), master=first_level)
        # user_factory.create_batch(7, hierarchy=hierarchy, master=second_level)
        for i in range(7):
            second_level.add_child(hierarchy=hierarchy, username='second_level{}'.format(i), master=second_level)
        user_factory.create_batch(55)

        url = reverse('tables-user')

        api_client.force_login(user=current_user)
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 19

    @pytest.mark.xfail
    def test_get_queryset_as_current_user_with_hierarchy_more_or_eq_2(self, api_login_client,
                                                                      user_factory, hierarchy_factory):
        high_hierarchy = hierarchy_factory(level=3)
        medium_hierarchy = hierarchy_factory(level=2)
        low_hierarchy = hierarchy_factory(level=1)
        user_factory.create_batch(10, hierarchy=low_hierarchy)
        user_factory.create_batch(10, hierarchy=high_hierarchy)
        current_user = user_factory(hierarchy=medium_hierarchy)

        url = reverse('tables-user')

        api_login_client.force_login(user=current_user)
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 22

    def test_create_user_with_all_fields(self, request, api_client, staff_user, user_data):
        url = reverse('users_v1_1-list')

        api_client.force_login(user=staff_user)
        user_data = get_values(user_data, request)
        response = api_client.post(url, data=user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        "field,code", FIELD_CODES, ids=[f[0] for f in FIELD_CODES])
    def test_create_user_without_one_field(self, request, api_client, staff_user, user_data, field, code):
        url = reverse('users_v1_1-list')

        user_data.pop(field)
        user_data = get_values(user_data, request)
        api_client.force_login(user=staff_user)
        response = api_client.post(url, data=user_data, format='json')

        assert response.status_code == code

    @pytest.mark.parametrize(
        "field,code", CHANGE_FIELD, ids=[f[0] for f in CHANGE_FIELD])
    def test_create_user_uniq_fields(
            self, request, api_client, staff_user,
            user_data, field, code):
        _user_data = get_values(user_data, request)

        changed_data = copy.deepcopy(user_data)
        _changed_data = get_values(changed_data, request)

        _changed_data[field] = change_field(_changed_data[field], changed_data[field], request)

        url = reverse('users_v1_1-list')

        api_client.force_login(user=staff_user)
        api_client.post(url, data=_user_data, format='json')
        response = api_client.post(url, data=_changed_data, format='json')

        assert response.status_code == code

    def test_create_root_user(self, api_client, staff_user, hierarchy_factory, department_factory):
        url = reverse('users_v1_1-list')

        api_client.force_login(user=staff_user)
        user_data = {
            'first_name': 'first',
            'last_name': 'last',
            'middle_name': 'middle',
            'language': 'en',
            'hierarchy': hierarchy_factory(level=100).id,
            'phone_number': '1234567890',
            'departments': (department_factory().id,),
        }
        response = api_client.post(url, data=user_data, format='json')

        # assert response.data == ''
        assert response.status_code == status.HTTP_201_CREATED

        new_user = CustomUser.objects.get(pk=response.data['id'])
        staff_user.refresh_from_db()

        assert len(new_user.path) == CustomUser.steplen
        assert new_user.depth == 1

    def test_create_user_with_parent(self, api_client, staff_user, hierarchy_factory, department_factory):
        url = reverse('users_v1_1-list')

        api_client.force_login(user=staff_user)
        user_data = {
            'first_name': 'first',
            'last_name': 'last',
            'middle_name': 'middle',
            'language': 'en',
            'hierarchy': hierarchy_factory(level=1).id,
            'master': staff_user.id,
            'phone_number': '1234567890',
            'departments': (department_factory().id,),
        }
        response = api_client.post(url, data=user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

        new_user = CustomUser.objects.get(pk=response.data['id'])
        staff_user.refresh_from_db()

        assert len(new_user.path) == CustomUser.steplen * 2
        assert new_user.path.startswith(staff_user.path)
        assert staff_user.numchild == 1
        assert new_user.depth == 2

    def test_move_user(self, user, api_login_client, user_factory):
        master = user_factory(username='master')
        user.move(master, 'last-child')
        user.refresh_from_db()
        child = user.add_child(master=user, username='child')

        new_master = user_factory(username='new_master')

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'master': new_master.id,
        }
        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        master.refresh_from_db()
        new_master.refresh_from_db()
        child.refresh_from_db()

        assert user.path.startswith(new_master.path)
        assert child.path.startswith(new_master.path)
        assert child.path.startswith(user.path)
        assert master.numchild == 0
        assert user.depth == 2
        assert child.depth == 3
        assert new_master.numchild == 1
        assert len(user.path) == CustomUser.steplen * 2
        assert len(child.path) == CustomUser.steplen * 3

    def test_move_user_to_root(self, api_login_client, user_factory, hierarchy_factory):
        master = user_factory(username='master')
        user = master.add_child(hierarchy=hierarchy_factory(level=100), master=master, username='user')
        child = user.add_child(master=user, username='child')

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'master': None,
        }
        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        master.refresh_from_db()
        child.refresh_from_db()

        assert master.numchild == 0
        assert user.depth == 1
        assert child.depth == 2
        assert len(user.path) == CustomUser.steplen
        assert len(child.path) == CustomUser.steplen * 2

    def test_move_user_to_descendant(self, api_login_client, user_factory):
        user = user_factory(username='user')
        new_master = user.add_child()

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'master': new_master.id,
        }
        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_user_with_all_fields(self, request, api_client, staff_user, user_data, user_factory):
        user_data = get_values(user_data, request)
        create_user_data = copy.deepcopy(user_data)
        divisions = create_user_data.pop('divisions')
        departments = create_user_data.pop('departments')

        create_user_data['hierarchy_id'] = create_user_data.pop('hierarchy')
        create_user_data['master_id'] = create_user_data.pop('master')
        create_user_data['born_date'] = strptime(create_user_data['born_date'])
        create_user_data['coming_date'] = strptime(create_user_data['coming_date'])
        create_user_data['repentance_date'] = strptime(create_user_data['repentance_date'])

        user = user_factory(**create_user_data)
        user.divisions.set(divisions)
        user.departments.set(departments)

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        api_client.force_login(user=staff_user)
        response = api_client.put(url, data=user_data, format='json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        'h1,h2', HIERARCHY_LEVELS_UP, ids=['{}->{}'.format(h[0], h[1]) for h in HIERARCHY_LEVELS_UP])
    def test_increase_or_unchange_hierarchy(self, h1, h2, api_client, staff_user, user_factory, hierarchy_factory):
        hierarchy_from = hierarchy_factory(level=h1)
        hierarchy_to = hierarchy_factory(level=h2)
        user = user_factory(hierarchy=hierarchy_from)

        api_client.force_login(user=staff_user)
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})
        response = api_client.patch(url, data={'hierarchy': hierarchy_to.id}, format='json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        'h1,h2', HIERARCHY_LEVELS_DOWN, ids=['{}->{}'.format(h[0], h[1]) for h in HIERARCHY_LEVELS_DOWN])
    def test_reduce_hierarchy_without_disciples(self, h1, h2, api_client, staff_user, user_factory, hierarchy_factory):
        hierarchy_from = hierarchy_factory(level=h1)
        hierarchy_to = hierarchy_factory(level=h2)
        user = user_factory(hierarchy=hierarchy_from)

        api_client.force_login(user=staff_user)
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})
        response = api_client.patch(url, data={'hierarchy': hierarchy_to.id}, format='json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        'h1,h2,l', get_hierarchies_down_correct(),
        ids=['{}->{} ({})'.format(h[0], h[1], h[2]) for h in get_hierarchies_down_correct()])
    def test_reduce_hierarchy_with_disciples_correct(
            self, h1, h2, l, api_client, staff_user, user_factory, hierarchy_factory):
        hierarchy_from = hierarchy_factory(level=h1)
        hierarchy_to = hierarchy_factory(level=h2)
        user = user_factory(hierarchy=hierarchy_from)
        # user_factory.create_batch(2, master=user, hierarchy__level=l)
        hierarchy = Hierarchy.objects.create(level=l, title='hhierarchy{}'.format(l))
        for i in range(2):
            user.add_child(hierarchy=hierarchy, username='user{}{}{}{}'.format(i, h1, h2, l), master=user)

        api_client.force_login(user=staff_user)
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})
        response = api_client.patch(url, data={'hierarchy': hierarchy_to.id}, format='json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        'h1,h2,l', get_hierarchies_down_incorrect(),
        ids=['{}->{} ({})'.format(h[0], h[1], h[2]) for h in get_hierarchies_down_incorrect()])
    def test_reduce_hierarchy_with_disciples_incorrect(
            self, h1, h2, l, api_client, staff_user, user_factory, hierarchy_factory):
        hierarchy_from = hierarchy_factory(level=h1)
        hierarchy_to = hierarchy_factory(level=h2)
        user = user_factory(hierarchy=hierarchy_from)
        # user_factory.create_batch(2, master=user, hierarchy__level=l)
        hierarchy = Hierarchy.objects.create(level=l, title='hhierarchy{}'.format(l))
        for i in range(2):
            user.add_child(hierarchy=hierarchy, username='user{}{}{}{}'.format(i, h1, h2, l), master=user)

        api_client.force_login(user=staff_user)
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})
        response = api_client.patch(url, data={'hierarchy': hierarchy_to.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        'h1,h2', HIERARCHY_LEVELS_DOWN, ids=['{}->{}'.format(h[0], h[1]) for h in HIERARCHY_LEVELS_DOWN])
    @pytest.mark.parametrize('l', ALL_HIERARCHIES)
    def test_status_reduce_hierarchy_with_disciples_and_move_to_master(
            self, h1, h2, l, api_client, staff_user, user_factory, hierarchy_factory):
        hierarchy_from = hierarchy_factory(level=h1)
        hierarchy_to = hierarchy_factory(level=h2)
        user = user_factory(hierarchy=hierarchy_from)
        other_user = user_factory()
        # user_factory.create_batch(2, master=user, hierarchy__level=l)
        hierarchy = Hierarchy.objects.create(level=l, title='hhierarchy{}'.format(l))
        for i in range(2):
            user.add_child(hierarchy=hierarchy, username='user{}{}{}{}'.format(i, h1, h2, l), master=user)

        api_client.force_login(user=staff_user)
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})
        data = {
            'hierarchy': hierarchy_to.id,
            'move_to_master': other_user.id,
        }
        response = api_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        'h1,h2', HIERARCHY_LEVELS_DOWN, ids=['{}->{}'.format(h[0], h[1]) for h in HIERARCHY_LEVELS_DOWN])
    @pytest.mark.parametrize('l', ALL_HIERARCHIES)
    def test_status_reduce_hierarchy_with_disciples_and_move_to_master_master_does_not_exist(
            self, h1, h2, l, api_client, staff_user, user_factory, hierarchy_factory):
        hierarchy_from = hierarchy_factory(level=h1)
        hierarchy_to = hierarchy_factory(level=h2)
        user = user_factory(hierarchy=hierarchy_from)
        # user_factory.create_batch(2, master=user, hierarchy__level=l)
        hierarchy = Hierarchy.objects.create(level=l, title='hhierarchy{}'.format(l))
        for i in range(2):
            user.add_child(hierarchy=hierarchy, username='user{}{}{}{}'.format(i, h1, h2, l), master=user)

        api_client.force_login(user=staff_user)
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})
        data = {
            'hierarchy': hierarchy_to.id,
            'move_to_master': 222222222,
        }
        response = api_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        'h1,h2', HIERARCHY_LEVELS_DOWN, ids=['{}->{}'.format(h[0], h[1]) for h in HIERARCHY_LEVELS_DOWN])
    @pytest.mark.parametrize('l', ALL_HIERARCHIES)
    def test_disciples_reduce_hierarchy_with_disciples_and_move_to_master_does_not_exist(
            self, h1, h2, l, api_client, staff_user, user_factory, hierarchy_factory):
        hierarchy_from = hierarchy_factory(level=h1)
        hierarchy_to = hierarchy_factory(level=h2)
        user = user_factory(hierarchy=hierarchy_from)
        other_user = user_factory()
        # user_factory.create_batch(2, master=user, hierarchy__level=l)
        hierarchy = Hierarchy.objects.create(level=l, title='hhierarchy{}'.format(l))
        for i in range(2):
            user.add_child(hierarchy=hierarchy, username='user{}{}{}{}'.format(i, h1, h2, l), master=user)
        assert user.disciples.exists()
        assert not other_user.disciples.exists()

        api_client.force_login(user=staff_user)
        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})
        data = {
            'hierarchy': hierarchy_to.id,
            'move_to_master': 222222222,
        }
        api_client.patch(url, data=data, format='json')

        assert user.disciples.exists()
        assert not other_user.disciples.exists()


@pytest.mark.django_db
class TestExistUserListViewSet:
    def test_without_params(self, api_client, user):
        url = reverse('exist_users-list')

        api_client.force_login(user=user)
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize('field', ['search_last_name', 'search_email', 'search_phone_number'])
    @pytest.mark.parametrize('value', ['', '2', '24', '246', '2468'])
    def test_with_param_length_less_than_5(self, api_client, user, field, value):
        url = reverse('exist_users-list')

        api_client.force_login(user=user)
        response = api_client.get(url, data={field: value}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize('field', ['search_last_name', 'search_email', 'search_phone_number'])
    def test_with_param_length_more_than_5(self, api_client, user, field):
        url = reverse('exist_users-list')

        api_client.force_login(user=user)
        response = api_client.get(url, data={field: 'value'}, format='json')

        assert response.status_code == status.HTTP_200_OK
