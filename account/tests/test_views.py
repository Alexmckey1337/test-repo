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
