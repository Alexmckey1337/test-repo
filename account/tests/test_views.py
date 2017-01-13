import datetime
import copy

from decimal import Decimal
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.factories import UserFactory
from account.models import CustomUser, AdditionalPhoneNumber
from hierarchy.factories import HierarchyFactory, DepartmentFactory
from partnership.factories import PartnerFactory
from status.factories import DivisionFactory
from status.models import Division


class TestNewUserViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory(username='testuser')
        self.DATA = {
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
            'department': DepartmentFactory().id,
            'master': UserFactory().id,
            'hierarchy': HierarchyFactory().id,
            'divisions': [d.id for d in DivisionFactory.create_batch(4)],
            'partner': {
                'value': 100,
                'responsible': PartnerFactory().id,
                'date': '2020-04-04',
            },
        }

    def test_partial_update_main_info(self):
        url = reverse('users_v1_1-detail', kwargs={'pk': self.user.id})

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
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_dict = dict(list(CustomUser.objects.filter(username='testuser').values(*data.keys()))[0])

        data['born_date'] = datetime.date(*map(lambda d: int(d), data['born_date'].split('-')))
        self.assertEqual(user_dict, data)

    def test_create_user_with_all_fields(self):
        url = reverse('users_v1_1-list')

        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_email(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('email')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_first_name(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('first_name')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_last_name(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('last_name')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_middle_name(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('middle_name')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_search_name(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('search_name')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_fb(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('facebook')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_vk(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('vkontakte')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_ok(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('odnoklassniki')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_skype(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('skype')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_phone_number(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('phone_number')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_additional_phones(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('additional_phones')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_born_date(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('born_date')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_coming_date(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('coming_date')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_repentance_date(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('repentance_date')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_country(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('country')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_region(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('region')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_city(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('city')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_district(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('district')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_address(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('address')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_department(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('department')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_master(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('master')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_hierarchy(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('hierarchy')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_divisions(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('divisions')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_partner(self):
        url = reverse('users_v1_1-list')

        self.DATA.pop('partner')
        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_partial_update_contact_info(self):
        url = reverse('users_v1_1-detail', kwargs={'pk': self.user.id})

        data = {
            'phone_number': '+380886664422',
            'additional_phones': '+380776664422',
            'email': 'test@email.com',
            'skype': 'skype',
            'facebook': 'http://fb.com/test',
            'vkontakte': 'http://vk.com/test',
            'odnoklassniki': 'http://ok.com/test',
        }
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        additional_phone = data.pop('additional_phones')
        user_dict = dict(list(CustomUser.objects.filter(username='testuser').values(*data.keys()))[0])

        self.assertEqual(user_dict, data)
        self.assertEqual(
            AdditionalPhoneNumber.objects.get(user__username='testuser').number,
            additional_phone)

    def test_partial_update_non_exist_additional_phone_number(self):
        user = UserFactory(username='otheruser')

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'additional_phones': '+380776664422',
        }
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        additional_phone = data.pop('additional_phones')
        self.assertEqual(
            AdditionalPhoneNumber.objects.get(user__username='otheruser').number,
            additional_phone)

    def test_partial_update_exist_additional_phone_number(self):
        user = UserFactory(username='otheruser')
        AdditionalPhoneNumber.objects.create(user=user, number='+380666666666')
        AdditionalPhoneNumber.objects.create(user=user, number='+380888888888')

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'additional_phones': '+380776664422',
        }
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        additional_phone = data.pop('additional_phones')
        self.assertEqual(
            AdditionalPhoneNumber.objects.filter(user__username='otheruser').first().number,
            additional_phone)

    def test_partial_update_exist_additional_phone_number_delete(self):
        user = UserFactory(username='otheruser')
        AdditionalPhoneNumber.objects.create(user=user, number='+380666666666')
        AdditionalPhoneNumber.objects.create(user=user, number='+380888888888')

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'additional_phones': '',
        }
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(
            AdditionalPhoneNumber.objects.filter(user__username='otheruser').exists())

    def test_partial_update_master_hierarchy_department(self):
        master = UserFactory(username='master')
        hierachy = HierarchyFactory()
        department = DepartmentFactory()

        url = reverse('users_v1_1-detail', kwargs={'pk': self.user.id})

        data = {
            'master': master.id,
            'hierarchy': hierachy.id,
            'department': department.id,
        }
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_dict = dict(list(CustomUser.objects.filter(username='testuser').values(*data.keys()))[0])

        self.assertEqual(user_dict, data)

    def test_user_list_filter_by_hierarchy(self):
        other_hierarchy = HierarchyFactory()
        hierarchy = HierarchyFactory()
        UserFactory.create_batch(10, hierarchy=hierarchy)
        UserFactory.create_batch(20, hierarchy=other_hierarchy)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get('{}?hierarchy={}'.format(url, hierarchy.id), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)

    def test_user_list_filter_by_department(self):
        other_department = DepartmentFactory()
        department = DepartmentFactory()
        UserFactory.create_batch(10, department=department)
        UserFactory.create_batch(20, department=other_department)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get('{}?department={}'.format(url, department.id), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)

    def test_user_list_filter_by_master(self):
        master = UserFactory(username='master')
        UserFactory.create_batch(10, master=master)
        UserFactory.create_batch(20)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get('{}?master={}'.format(url, master.id), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)

    def test_user_list_filter_by_multi_master(self):
        master = UserFactory(username='master')
        other_master = UserFactory(username='other_master')
        UserFactory.create_batch(10, master=master)
        UserFactory.create_batch(40, master=other_master)
        UserFactory.create_batch(20)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get(
            '{}?master={}&master={}'.format(url, master.id, other_master.id),
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 50)

    def test_user_search_by_fio(self):
        UserFactory.create_batch(10)
        user = UserFactory(last_name='searchlast', first_name='searchfirst')

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get(
            '{}?search_fio={}'.format(url, 'searchfirst searchlast'),
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_user_search_by_email(self):
        UserFactory.create_batch(10)
        UserFactory(email='mysupermail@test.com')
        UserFactory(email='test@mysupermail.com')

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get(
            '{}?search_email={}'.format(url, 'mysupermail'),
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_user_search_by_phone(self):
        UserFactory.create_batch(10)
        UserFactory(phone_number='+380990002246')
        UserFactory(phone_number='+380992299000')

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get(
            '{}?search_phone_number={}'.format(url, '99000'),
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_user_search_by_country(self):
        UserFactory.create_batch(10)
        UserFactory.create_batch(8, country='Ukraine')

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get(
            '{}?search_country={}'.format(url, 'Ukraine'),
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 8)

    def test_user_search_by_city(self):
        UserFactory.create_batch(10)
        UserFactory.create_batch(8, city='Tokio')

        url = reverse('users_v1_1-list')

        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.get(
            '{}?search_city={}'.format(url, 'Tokio'),
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 8)

    def test_current_user_as_pk(self):
        UserFactory.create_batch(10)
        current_user = UserFactory(is_staff=True)

        url = reverse('users_v1_1-detail', kwargs={'pk': 'current'})

        self.client.force_login(user=current_user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], current_user.id)

    def test_get_queryset_as_staff_current_user(self):
        UserFactory.create_batch(10)
        current_user = UserFactory(is_staff=True)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=current_user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 14)

    def test_get_queryset_as_current_user_without_hierarchy(self):
        UserFactory.create_batch(10)
        current_user = UserFactory(hierarchy=None)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=current_user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_get_queryset_as_current_user_with_hierarchy_less_then_2(self):
        hierarchy = HierarchyFactory(level=1)
        current_user = UserFactory(hierarchy=hierarchy)
        first_level = UserFactory(hierarchy=hierarchy, master=current_user)
        second_level = UserFactory(hierarchy=hierarchy, master=first_level)
        UserFactory(hierarchy=hierarchy, master=current_user)
        UserFactory.create_batch(8, hierarchy=hierarchy, master=first_level)
        UserFactory.create_batch(7, hierarchy=hierarchy, master=second_level)
        UserFactory.create_batch(55)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=current_user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 19)

    def test_get_queryset_as_current_user_with_hierarchy_more_or_eq_2(self):
        high_hierarchy = HierarchyFactory(level=3)
        medium_hierarchy = HierarchyFactory(level=2)
        low_hierarchy = HierarchyFactory(level=1)
        UserFactory.create_batch(10, hierarchy=low_hierarchy)
        UserFactory.create_batch(10, hierarchy=high_hierarchy)
        current_user = UserFactory(hierarchy=medium_hierarchy)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=current_user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 24)

    def test_update_user_with_all_fields(self):
        user_data = copy.deepcopy(self.DATA)
        additional_phones = user_data.pop('additional_phones')
        divisions = user_data.pop('divisions')
        partner = user_data.pop('partner')

        user_data['department_id'] = user_data.pop('department')
        user_data['hierarchy_id'] = user_data.pop('hierarchy')
        user_data['master_id'] = user_data.pop('master')
        user_data['born_date'] = datetime.date(*map(lambda d: int(d), user_data['born_date'].split('-')))
        user_data['coming_date'] = datetime.date(*map(lambda d: int(d), user_data['coming_date'].split('-')))
        user_data['repentance_date'] = datetime.date(*map(lambda d: int(d), user_data['repentance_date'].split('-')))

        user = UserFactory(**user_data)
        PartnerFactory(
            user=user,
            value=Decimal(partner['value']),
            date=datetime.date(*map(lambda d: int(d), partner['date'].split('-'))),
            responsible_id=partner['responsible'])
        AdditionalPhoneNumber.objects.create(user=user, number=additional_phones)
        user.divisions.set(divisions)

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = self.DATA
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
