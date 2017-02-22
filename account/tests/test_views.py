import copy
import datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from account.models import CustomUser

FIELD_CODES = (
    # optional fields
    ('email', 201),
    ('middle_name', 201),
    ('search_name', 201),
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
    ('partner', 201),
    ('spiritual_level', 201),

    # required fields
    ('first_name', 400),
    ('last_name', 400),
    ('phone_number', 400),
    ('department', 400),
    ('master', 400),
    ('hierarchy', 400),
)


@pytest.mark.django_db
class TestNewUserViewSet:
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
        hierachy = hierarchy_factory()
        department = department_factory()

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'master': master.id,
            'hierarchy': hierachy.id,
            'department': department.id,
        }
        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.patch(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

        user_dict = dict(list(CustomUser.objects.filter(username='testuser').values(*data.keys()))[0])

        assert user_dict == data

    def test_user_list_filter_by_hierarchy(self, api_login_client, user_factory, hierarchy_factory):
        other_hierarchy = hierarchy_factory()
        hierarchy = hierarchy_factory()
        user_factory.create_batch(10, hierarchy=hierarchy)
        user_factory.create_batch(20, hierarchy=other_hierarchy)

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?hierarchy={}'.format(url, hierarchy.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_department(self, api_login_client, user_factory, department_factory):
        other_department = department_factory()
        department = department_factory()
        user_factory.create_batch(10, department=department)
        user_factory.create_batch(20, department=other_department)

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?department={}'.format(url, department.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_master(self, api_login_client, user_factory):
        master = user_factory(username='master')
        user_factory.create_batch(10, master=master)
        user_factory.create_batch(20)

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?master={}'.format(url, master.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_multi_master(self, api_login_client, user_factory):
        master = user_factory(username='master')
        other_master = user_factory(username='other_master')
        user_factory.create_batch(10, master=master)
        user_factory.create_batch(40, master=other_master)
        user_factory.create_batch(20)

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?master={}&master={}'.format(url, master.id, other_master.id),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 50

    def test_user_search_by_fio(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        user_factory(last_name='searchlast', first_name='searchfirst')

        url = reverse('users_v1_1-list')

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

        url = reverse('users_v1_1-list')

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

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_phone_number={}'.format(url, '99000'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_country(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        user_factory.create_batch(8, country='Ukraine')

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_country={}'.format(url, 'Ukraine'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_user_search_by_city(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        user_factory.create_batch(8, city='Tokio')

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_city={}'.format(url, 'Tokio'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_current_user_as_pk_v1_0(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        current_user = user_factory(is_staff=True)

        url = reverse('customuser-detail', kwargs={'pk': 'current'})

        api_login_client.force_login(user=current_user)
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == current_user.id

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

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=current_user)
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 12

    def test_get_queryset_as_current_user_without_hierarchy(self, api_login_client, user_factory):
        user_factory.create_batch(10)
        current_user = user_factory(hierarchy=None)

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=current_user)
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_get_queryset_as_current_user_with_hierarchy_less_then_2(self, api_client, user_factory,
                                                                     hierarchy_factory):
        hierarchy = hierarchy_factory(level=1)
        current_user = user_factory(hierarchy=hierarchy)
        first_level = user_factory(hierarchy=hierarchy, master=current_user)
        second_level = user_factory(hierarchy=hierarchy, master=first_level)
        user_factory(hierarchy=hierarchy, master=current_user)
        user_factory.create_batch(8, hierarchy=hierarchy, master=first_level)
        user_factory.create_batch(7, hierarchy=hierarchy, master=second_level)
        user_factory.create_batch(55)

        url = reverse('users_v1_1-list')

        api_client.force_login(user=current_user)
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 19

    def test_get_queryset_as_current_user_with_hierarchy_more_or_eq_2(self, api_login_client,
                                                                      user_factory, hierarchy_factory):
        high_hierarchy = hierarchy_factory(level=3)
        medium_hierarchy = hierarchy_factory(level=2)
        low_hierarchy = hierarchy_factory(level=1)
        user_factory.create_batch(10, hierarchy=low_hierarchy)
        user_factory.create_batch(10, hierarchy=high_hierarchy)
        current_user = user_factory(hierarchy=medium_hierarchy)

        url = reverse('users_v1_1-list')

        api_login_client.force_login(user=current_user)
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 22

    def test_create_user_with_all_fields(self, api_client, staff_user, user_data):
        url = reverse('users_v1_1-list')

        api_client.force_login(user=staff_user)
        response = api_client.post(url, data=user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        "field,code", FIELD_CODES, ids=[f[0] for f in FIELD_CODES])
    def test_create_user_without_one_field(self, api_client, staff_user, user_data, field, code):
        url = reverse('users_v1_1-list')

        user_data.pop(field)
        api_client.force_login(user=staff_user)
        response = api_client.post(url, data=user_data, format='json')

        assert response.status_code == code

    def test_update_user_with_all_fields(self, api_client, staff_user, user_data, user_factory, partner_factory):
        create_user_data = copy.deepcopy(user_data)
        divisions = create_user_data.pop('divisions')
        partner = create_user_data.pop('partner')

        create_user_data['department_id'] = create_user_data.pop('department')
        create_user_data['hierarchy_id'] = create_user_data.pop('hierarchy')
        create_user_data['master_id'] = create_user_data.pop('master')
        create_user_data['born_date'] = datetime.date(
            *map(lambda d: int(d), create_user_data['born_date'].split('-')))
        create_user_data['coming_date'] = datetime.date(
            *map(lambda d: int(d), create_user_data['coming_date'].split('-')))
        create_user_data['repentance_date'] = datetime.date(
            *map(lambda d: int(d), create_user_data['repentance_date'].split('-')))

        user = user_factory(**create_user_data)
        partner_factory(
            user=user,
            value=Decimal(partner['value']),
            date=datetime.date(*map(lambda d: int(d), partner['date'].split('-'))),
            responsible_id=partner['responsible'])
        user.divisions.set(divisions)

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        api_client.force_login(user=staff_user)
        response = api_client.put(url, data=user_data, format='json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("data,code", [
        ([1, 2], status.HTTP_400_BAD_REQUEST),
        ({'d': [1, 2]}, status.HTTP_400_BAD_REQUEST),
        ({'divisions': '1,2'}, status.HTTP_400_BAD_REQUEST),
        ({'divisions': [111, 222]}, status.HTTP_400_BAD_REQUEST),
        (None, status.HTTP_200_OK)
    ], ids=['non_dict', 'without_divisions', 'divisions_not_list', 'incorrect_divisions_id', 'correct'])
    def test_set_divisions_code(self, api_client, staff_user, user, divisions, data, code):
        url = reverse('users_v1_1-set-divisions', kwargs={'pk': user.id})

        data = data or {'divisions': [d.id for d in divisions]}

        api_client.force_login(user=staff_user)
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == code

    def test_set_divisions(self, api_client, staff_user, user, divisions):
        url = reverse('users_v1_1-set-divisions', kwargs={'pk': user.id})

        data = {'divisions': [d.id for d in divisions]}

        api_client.force_login(user=staff_user)
        api_client.post(url, data=data, format='json')

        assert list(user.divisions.values_list('id', flat=True)) == data['divisions']

    def test_create_partner_already_exist(self, api_client, staff_user, partner, currency):
        user = partner.user
        url = reverse('users_v1_1-create-partner', kwargs={'pk': user.id})

        partner_data = {
            'value': 100,
            'date': '2000-11-13',
            'currency': currency.id
        }

        api_client.force_login(user=staff_user)
        response = api_client.post(url, data=partner_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_partner_with_incorrect_data_format(self, api_client, staff_user, user):
        url = reverse('users_v1_1-create-partner', kwargs={'pk': user.id})

        partner_data = 'incorrect'

        api_client.force_login(user=staff_user)
        response = api_client.post(url, data=partner_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_partner_with_incorrect_data(self, api_client, staff_user, user):
        url = reverse('users_v1_1-create-partner', kwargs={'pk': user.id})

        partner_data = {
            'value'
        }

        api_client.force_login(user=staff_user)
        response = api_client.post(url, data=partner_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_partner_with_correct_data(self, api_client, staff_user, user):
        url = reverse('users_v1_1-create-partner', kwargs={'pk': user.id})

        partner_data = {}

        api_client.force_login(user=staff_user)
        response = api_client.post(url, data=partner_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_update_partner_does_not_exist(self, api_client, staff_user, user, currency):
        url = reverse('users_v1_1-update-partner', kwargs={'pk': user.id})

        partner_data = {
            'value': 100,
            'date': '2000-11-13',
            'currency': currency.id
        }

        api_client.force_login(user=staff_user)
        response = api_client.put(url, data=partner_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_partner_with_incorrect_data_format(self, api_client, staff_user, partner):
        user = partner.user
        url = reverse('users_v1_1-update-partner', kwargs={'pk': user.id})

        partner_data = 'incorrect'

        api_client.force_login(user=staff_user)
        response = api_client.put(url, data=partner_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_partner_with_incorrect_data(self, api_client, staff_user, partner):
        user = partner.user
        url = reverse('users_v1_1-update-partner', kwargs={'pk': user.id})

        partner_data = {
            'value'
        }

        api_client.force_login(user=staff_user)
        response = api_client.put(url, data=partner_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_partner_with_correct_data(self, api_client, staff_user, partner):
        user = partner.user
        url = reverse('users_v1_1-update-partner', kwargs={'pk': user.id})

        partner_data = {}

        api_client.force_login(user=staff_user)
        response = api_client.put(url, data=partner_data, format='json')

        assert response.status_code == status.HTTP_200_OK
