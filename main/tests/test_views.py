# -*- coding: utf-8
from __future__ import unicode_literals

from unittest import skip

from django.core.urlresolvers import reverse
from django.test import TestCase

from account.factories import UserFactory
from event.factories import MeetingTypeFactory
from event.models import MeetingType
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
        UserFactory.create_batch(4, hierarchy=h1, master=self.login_user)  # in masters +4 = 5
        UserFactory.create_batch(4, hierarchy=h1)
        m1 = UserFactory(hierarchy=h1, master=self.login_user)  # in masters +1 = 6
        m2 = UserFactory(hierarchy=h1, master=self.login_user)  # in masters +1 = 7
        m3 = UserFactory(hierarchy=h1)
        UserFactory.create_batch(3, hierarchy=h1, master=m1)  # in masters +3 = 10
        UserFactory.create_batch(3, hierarchy=h1, master=m2)  # in masters +3 = 13
        UserFactory.create_batch(3, hierarchy=h1, master=m3)
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['masters']), 13)

    def test_masters_in_context_user_with_hierarchy_level_more_or_eq_2(self):
        h1 = HierarchyFactory(level=1)
        h2 = HierarchyFactory(level=2)
        self.login_user.hierarchy = h2
        self.login_user.save()  # in masters +1 = 1
        UserFactory.create_batch(4, hierarchy=h1, master=self.login_user)  # in masters +4 = 5
        UserFactory.create_batch(4, hierarchy=h1)  # in masters +4 = 9
        m1 = UserFactory(hierarchy=h1, master=self.login_user)  # in masters +1 = 10
        m2 = UserFactory(hierarchy=h1, master=self.login_user)  # in masters +1 = 11
        m3 = UserFactory(hierarchy=h1)  # in masters +1 = 12
        UserFactory.create_batch(3, hierarchy=h1, master=m1)  # in masters +3 = 15
        UserFactory.create_batch(3, hierarchy=h1, master=m2)  # in masters +3 = 18
        UserFactory.create_batch(3, hierarchy=h1, master=m3)  # in masters +3 = 21
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['masters']), 21)


class TestMeetingTypeListPage(LoginUserMixin):
    def setUp(self):
        super(TestMeetingTypeListPage, self).setUp()
        self.url = reverse('meeting_type:list')

    def test_meeting_types_in_context(self):
        response = self.client.get(self.url)

        self.assertEqual(
            list(response.context['meeting_types']),
            list(MeetingType.objects.all())
        )


class TestMeetingTypeDetailPage(LoginUserMixin):
    def setUp(self):
        super(TestMeetingTypeDetailPage, self).setUp()
        self.meeting_type = MeetingTypeFactory()
        self.url = reverse('meeting_type:detail', kwargs={'code': self.meeting_type.code})

    def test_meeting_type_in_context(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.context['meeting_type'],
            self.meeting_type
        )


class TestCreateMeetingReportPage(LoginUserMixin):
    def setUp(self):
        super(TestCreateMeetingReportPage, self).setUp()
        self.meeting_type = MeetingTypeFactory()
        self.url = reverse('meeting_type:report', kwargs={'code': self.meeting_type.code})

    def test_with_login_user(self):
        pass

    def test_with_user_hierarchy_level_less_1(self):
        self.login_user.hierarchy = HierarchyFactory(level=0)
        self.login_user.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_with_user_without_hierarchy_level(self):
        self.login_user.hierarchy = None
        self.login_user.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_meeting_type_in_context_with_user_hierarchy_level_eq_1(self):
        self.login_user.hierarchy = HierarchyFactory(level=1)
        self.login_user.save()
        response = self.client.get(self.url)

        self.assertEqual(
            response.context['meeting_type'],
            self.meeting_type
        )

    def test_meeting_type_in_context_with_user_hierarchy_level_more_1(self):
        self.login_user.hierarchy = HierarchyFactory(level=4)
        self.login_user.save()
        response = self.client.get(self.url)

        self.assertEqual(
            response.context['meeting_type'],
            self.meeting_type
        )

    @skip("Deprecated")
    def test_leaders_in_context_with_user_hierarchy_level_eq_1(self):
        self.login_user.hierarchy = HierarchyFactory(level=1)
        self.login_user.save()
        hierarchy = HierarchyFactory(level=0)
        other_hierarchy = HierarchyFactory(level=1)
        UserFactory.create_batch(11, hierarchy=hierarchy, master=self.login_user)
        UserFactory.create_batch(4, hierarchy=other_hierarchy)

        response = self.client.get(self.url)

        self.assertEqual(response.context.get('leaders', 'NaN'), 'NaN')

    @skip("Deprecated")
    def test_leaders_in_context_with_user_hierarchy_level_more_1(self):
        self.login_user.hierarchy = HierarchyFactory(level=3)
        self.login_user.save()

        first_hierarchy = HierarchyFactory(level=1)
        second_hierarchy = HierarchyFactory(level=2)
        UserFactory.create_batch(2, hierarchy=second_hierarchy, master=self.login_user)
        s1 = UserFactory(hierarchy=second_hierarchy, master=self.login_user)
        s2 = UserFactory(hierarchy=second_hierarchy, master=self.login_user)
        UserFactory.create_batch(6, hierarchy=first_hierarchy, master=s1)
        UserFactory.create_batch(4, hierarchy=first_hierarchy, master=s2)
        UserFactory.create_batch(7, hierarchy=first_hierarchy, master=s2)

        other_s = UserFactory(hierarchy=second_hierarchy)
        UserFactory.create_batch(6, hierarchy=first_hierarchy, master=other_s)

        response = self.client.get(self.url)

        self.assertEqual(len(response.context.get('leaders')), 17)
