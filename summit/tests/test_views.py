from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.factories import UserFactory
from summit.factories import SummitFactory, SummitLessonFactory, SummitAnketFactory
from summit.models import Summit, SummitLesson, SummitAnket
from summit.serializers import SummitSerializer, SummitLessonSerializer, SummitAnketForSelectSerializer


class TestSummitViewSet(APITestCase):
    def setUp(self):
        self.summit = SummitFactory()

    def test_get_detail_anon(self):
        url = reverse('summit-detail', kwargs={'pk': self.summit.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_detail(self):
        url = reverse('summit-detail', kwargs={'pk': self.summit.id})
        self.client.force_login(user=UserFactory())
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, SummitSerializer(self.summit).data)

    def test_get_list_without_pagination(self):
        SummitFactory.create_batch(9)
        url = reverse('summit-list')
        self.client.force_login(user=UserFactory())
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'],
                         SummitSerializer(Summit.objects.order_by('-start_date'), many=True).data)

    def test_get_list_with_pagination(self):
        SummitFactory.create_batch(44)
        url = reverse('summit-list')
        self.client.force_login(user=UserFactory())
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 30)
        self.assertEqual(response.data['count'], 45)

    def test_create_summit(self):
        url = reverse('summit-list')
        self.client.force_login(user=UserFactory())
        response = self.client.post(url, data={}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_summit(self):
        url = reverse('summit-detail', kwargs={'pk': self.summit.id})
        self.client.force_login(user=UserFactory())

        response = self.client.put(url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_summit(self):
        url = reverse('summit-detail', kwargs={'pk': self.summit.id})
        self.client.force_login(user=UserFactory())

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_lessons(self):
        SummitLessonFactory.create_batch(6, summit=self.summit)
        url = reverse('summit-lessons', kwargs={'pk': self.summit.id})
        self.client.force_login(user=UserFactory())

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            SummitLessonSerializer(SummitLesson.objects.all(), many=True).data)

    def test_add_new_lesson(self):
        url = reverse('summit-add-lesson', kwargs={'pk': self.summit.id})
        self.client.force_login(user=UserFactory())

        response = self.client.post(url, data={'name': 'New lesson'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, SummitLessonSerializer(self.summit.lessons.get()).data)

    def test_get_consultants(self):
        SummitAnketFactory.create_batch(6, summit=self.summit, role=SummitAnket.CONSULTANT)
        url = reverse('summit-consultants', kwargs={'pk': self.summit.id})
        self.client.force_login(user=UserFactory())

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            SummitAnketForSelectSerializer(SummitAnket.objects.order_by('-id'), many=True).data)

    def test_add_consultant_supervisor(self):
        url = reverse('summit-add-consultant', kwargs={'pk': self.summit.id})
        user = UserFactory()
        SummitAnketFactory(user=user, role=SummitAnket.SUPERVISOR, summit=self.summit)
        self.client.force_login(user=user)

        anket = SummitAnketFactory(summit=self.summit)
        response = self.client.post(url, data={'anket_id': anket.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {'summit_id': self.summit.id, 'consultant_id': anket.id, 'action': 'added'})
        self.assertEqual(SummitAnket.objects.get(id=anket.id).role, SummitAnket.CONSULTANT)

    def test_add_consultant_consultant(self):
        url = reverse('summit-add-consultant', kwargs={'pk': self.summit.id})
        user = UserFactory()
        SummitAnketFactory(user=user, role=SummitAnket.CONSULTANT, summit=self.summit)
        self.client.force_login(user=user)

        anket = SummitAnketFactory(summit=self.summit)
        response = self.client.post(url, data={'anket_id': anket.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_consultant_to_other_summit(self):
        url = reverse('summit-add-consultant', kwargs={'pk': self.summit.id})
        user = UserFactory()
        SummitAnketFactory(user=user, role=SummitAnket.SUPERVISOR, summit=self.summit)
        self.client.force_login(user=user)

        anket = SummitAnketFactory(summit=SummitFactory())
        response = self.client.post(url, data={'anket_id': anket.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_del_consultant_supervisor(self):
        url = reverse('summit-del-consultant', kwargs={'pk': self.summit.id})
        user = UserFactory()
        SummitAnketFactory(user=user, role=SummitAnket.SUPERVISOR, summit=self.summit)
        self.client.force_login(user=user)

        anket = SummitAnketFactory(summit=self.summit)
        response = self.client.post(url, data={'anket_id': anket.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            response.data,
            {'summit_id': self.summit.id, 'consultant_id': anket.id, 'action': 'removed'})
        self.assertEqual(SummitAnket.objects.get(id=anket.id).role, SummitAnket.VISITOR)

    def test_del_consultant_consultant(self):
        url = reverse('summit-del-consultant', kwargs={'pk': self.summit.id})
        user = UserFactory()
        SummitAnketFactory(user=user, role=SummitAnket.CONSULTANT, summit=self.summit)
        self.client.force_login(user=user)

        anket = SummitAnketFactory(summit=self.summit)
        response = self.client.post(url, data={'anket_id': anket.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_del_consultant_to_other_summit(self):
        url = reverse('summit-del-consultant', kwargs={'pk': self.summit.id})
        user = UserFactory()
        SummitAnketFactory(user=user, role=SummitAnket.SUPERVISOR, summit=self.summit)
        self.client.force_login(user=user)

        anket = SummitAnketFactory(summit=SummitFactory())
        response = self.client.post(url, data={'anket_id': anket.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
