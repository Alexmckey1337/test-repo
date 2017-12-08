# -*- coding: utf-8
from __future__ import unicode_literals

import pytest
from django.urls import reverse
from django.test import TestCase

from account.factories import UserFactory
from hierarchy.factories import HierarchyFactory, DepartmentFactory
from hierarchy.models import Department, Hierarchy


class LoginUserMixin(TestCase):
    def setUp(self):
        self.url = '/'
        self.login_user = UserFactory()
        self.client.force_login(user=self.login_user)

    def test_with_anon_user(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_with_login_user(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestDatabasePage(LoginUserMixin):
    def setUp(self):
        super(TestDatabasePage, self).setUp()
        self.url = reverse('index')

    def test_departments_in_context(self):
        DepartmentFactory.create_batch(6)
        response = self.client.get(self.url)

        self.assertEqual(
            list(response.context['departments']),
            list(Department.objects.all())
        )

    def test_hierarchies_in_context(self):
        HierarchyFactory.create_batch(3)
        response = self.client.get(self.url)

        self.assertEqual(
            list(response.context['hierarchies']),
            list(Hierarchy.objects.order_by('level'))
        )

    def test_masters_in_context_user_is_staff(self):
        h0 = HierarchyFactory(level=0)
        h2 = HierarchyFactory(level=2)
        self.login_user.is_staff = True
        self.login_user.hierarchy = h0
        self.login_user.save()
        UserFactory.create_batch(11, hierarchy=h2)  # in masters +11 = 11
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['masters']), 11)

    def test_masters_in_context_user_without_hierarchy(self):
        h0 = HierarchyFactory(level=0)
        self.login_user.hierarchy = None
        self.login_user.save()
        UserFactory.create_batch(11, hierarchy=h0)
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['masters']), 0)

    def test_masters_in_context_user_with_hierarchy_level_less_2(self):
        h1 = HierarchyFactory(level=1)
        self.login_user.hierarchy = h1
        self.login_user.save()  # in masters +1 = 1
        # UserFactory.create_batch(4, hierarchy=h1, master=self.login_user)  # in masters +4 = 5
        for i in range(4):
            self.login_user.add_child(username='user{}'.format(i), hierarchy=h1, master=self.login_user)
        UserFactory.create_batch(4, hierarchy=h1)
        # m1 = UserFactory(hierarchy=h1, master=self.login_user)  # in masters +1 = 6
        m1 = self.login_user.add_child(username='m1user', hierarchy=h1, master=self.login_user)
        # m2 = UserFactory(hierarchy=h1, master=self.login_user)  # in masters +1 = 7
        m2 = self.login_user.add_child(username='m2user', hierarchy=h1, master=self.login_user)
        m3 = UserFactory(hierarchy=h1)
        # UserFactory.create_batch(3, hierarchy=h1, master=m1)  # in masters +3 = 10
        for i in range(3):
            m1.add_child(username='m1user{}'.format(i), hierarchy=h1, master=m1)
        # UserFactory.create_batch(3, hierarchy=h1, master=m2)  # in masters +3 = 13
        for i in range(3):
            m2.add_child(username='m2user{}'.format(i), hierarchy=h1, master=m2)
        # UserFactory.create_batch(3, hierarchy=h1, master=m3)
        for i in range(3):
            m3.add_child(username='m3user{}'.format(i), hierarchy=h1, master=m3)
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['masters']), 13)

    def test_masters_in_context_user_with_hierarchy_level_more_or_eq_2(self):
        h1 = HierarchyFactory(level=1)
        h2 = HierarchyFactory(level=2)
        self.login_user.hierarchy = h2
        self.login_user.save()  # in masters +1 = 1
        # UserFactory.create_batch(4, hierarchy=h1, master=self.login_user)  # in masters +4 = 5
        for i in range(4):
            self.login_user.add_child(username='user{}'.format(i), hierarchy=h1, master=self.login_user)
        UserFactory.create_batch(4, hierarchy=h1)  # in masters +4 = 9
        # m1 = UserFactory(hierarchy=h1, master=self.login_user)  # in masters +1 = 10
        m1 = self.login_user.add_child(username='m1user', hierarchy=h1, master=self.login_user)
        # m2 = UserFactory(hierarchy=h1, master=self.login_user)  # in masters +1 = 11
        m2 = self.login_user.add_child(username='m2user', hierarchy=h1, master=self.login_user)
        m3 = UserFactory(hierarchy=h1)  # in masters +1 = 12
        # UserFactory.create_batch(3, hierarchy=h1, master=m1)  # in masters +3 = 15
        for i in range(3):
            m1.add_child(username='m1user{}'.format(i), hierarchy=h1, master=m1)
        # UserFactory.create_batch(3, hierarchy=h1, master=m2)  # in masters +3 = 18
        for i in range(3):
            m2.add_child(username='m2user{}'.format(i), hierarchy=h1, master=m2)
        # UserFactory.create_batch(3, hierarchy=h1, master=m3)  # in masters +3 = 21
        for i in range(3):
            m3.add_child(username='m3user{}'.format(i), hierarchy=h1, master=m3)
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['masters']), 21)


@pytest.mark.urls('main.tests.urls')
@pytest.mark.django_db
class TestDealPaymentView:
    def test_variable_in_context_code(self, client, deal):
        url = '/payment/deal/{}/'.format(deal.id)
        response = client.get(url)
        assert response.status_code == 302

    @pytest.mark.parametrize('variable', ['payments', 'deal', 'partners'])
    def test_variable_in_context(self, login_client, deal, variable):
        url = '/payment/deal/{}/'.format(deal.id)
        response = login_client.get(url)
        assert variable in response.context.keys()


@pytest.mark.urls('main.tests.urls')
@pytest.mark.django_db
class TestPartnerPaymentView:
    def test_variable_in_context_code(self, client, deal):
        url = '/payment/deal/{}/'.format(deal.id)
        response = client.get(url)
        assert response.status_code == 302
