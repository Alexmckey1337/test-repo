import datetime

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.factories import UserFactory
from account.models import CustomUser, AdditionalPhoneNumber
from hierarchy.factories import HierarchyFactory, DepartmentFactory


class TestNewUserViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory(username='testuser')

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

    def test_partial_update_contact_info(self):
        url = reverse('users_v1_1-detail', kwargs={'pk': self.user.id})

        data = {
            'phone_number': '+380886664422',
            'additional_phone': '+380776664422',
            'email': 'test@email.com',
            'skype': 'skype',
            'facebook': 'http://fb.com/test',
            'vkontakte': 'http://vk.com/test',
            'odnoklassniki': 'http://ok.com/test',
        }
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        additional_phone = data.pop('additional_phone')
        user_dict = dict(list(CustomUser.objects.filter(username='testuser').values(*data.keys()))[0])

        self.assertEqual(user_dict, data)
        self.assertEqual(
            AdditionalPhoneNumber.objects.get(user__username='testuser').number,
            additional_phone)

    def test_partial_update_non_exist_additional_phone_number(self):
        user = UserFactory(username='otheruser')

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'additional_phone': '+380776664422',
        }
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        additional_phone = data.pop('additional_phone')
        self.assertEqual(
            AdditionalPhoneNumber.objects.get(user__username='otheruser').number,
            additional_phone)

    def test_partial_update_exist_additional_phone_number(self):
        user = UserFactory(username='otheruser')
        AdditionalPhoneNumber.objects.create(user=user, number='+380666666666')
        AdditionalPhoneNumber.objects.create(user=user, number='+380888888888')

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'additional_phone': '+380776664422',
        }
        self.client.force_login(user=UserFactory(is_staff=True))
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        additional_phone = data.pop('additional_phone')
        self.assertEqual(
            AdditionalPhoneNumber.objects.filter(user__username='otheruser').first().number,
            additional_phone)

    def test_partial_update_exist_additional_phone_number_delete(self):
        user = UserFactory(username='otheruser')
        AdditionalPhoneNumber.objects.create(user=user, number='+380666666666')
        AdditionalPhoneNumber.objects.create(user=user, number='+380888888888')

        url = reverse('users_v1_1-detail', kwargs={'pk': user.id})

        data = {
            'additional_phone': '',
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
        self.assertEqual(response.data['count'], 12)

    def test_get_queryset_as_current_user_without_hierarchy(self):
        UserFactory.create_batch(10)
        current_user = UserFactory(hierarchy=None)

        url = reverse('users_v1_1-list')

        self.client.force_login(user=current_user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_get_queryset_as_current_user_with_hierarchy(self):
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
        self.assertEqual(response.data['count'], 10)
