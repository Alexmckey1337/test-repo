import pytest
from django.core.urlresolvers import reverse
from rest_framework import status

from summit.models import Summit, SummitLesson, SummitAnket
from summit.serializers import SummitSerializer, SummitLessonSerializer, SummitAnketForSelectSerializer


@pytest.mark.django_db
class TestSummitViewSet:
    def test_get_detail_anon(self, api_client, summit):
        url = reverse('summit-detail', kwargs={'pk': summit.id})
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_detail(self, api_login_client, summit):
        url = reverse('summit-detail', kwargs={'pk': summit.id})
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == SummitSerializer(summit).data

    def test_get_list_without_pagination(self, api_login_client, summit_factory):
        summit_factory.create_batch(9)
        url = reverse('summit-list')
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == SummitSerializer(Summit.objects.order_by('-start_date'), many=True).data

    def test_get_list_with_pagination(self, api_login_client, summit_factory):
        summit_factory.create_batch(44)
        url = reverse('summit-list')
        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 30
        assert response.data['count'] == 44

    def test_create_summit(self, api_login_client):
        url = reverse('summit-list')
        response = api_login_client.post(url, data={}, format='json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_summit(self, api_login_client, summit):
        url = reverse('summit-detail', kwargs={'pk': summit.id})

        response = api_login_client.put(url, data={}, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response = api_login_client.patch(url, data={}, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_summit(self, api_login_client, summit):
        url = reverse('summit-detail', kwargs={'pk': summit.id})

        response = api_login_client.delete(url, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_get_lessons(self, api_login_client, summit, summit_lesson_factory):
        summit_lesson_factory.create_batch(6, summit=summit)
        url = reverse('summit-lessons', kwargs={'pk': summit.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == SummitLessonSerializer(SummitLesson.objects.all(), many=True).data

    def test_add_new_lesson(self, api_login_client, summit):
        url = reverse('summit-add-lesson', kwargs={'pk': summit.id})

        response = api_login_client.post(url, data={'name': 'New lesson'}, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == SummitLessonSerializer(summit.lessons.get()).data

    def test_get_consultants(self, api_login_client, summit, summit_anket_factory):
        summit_anket_factory.create_batch(6, summit=summit, role=SummitAnket.CONSULTANT)
        url = reverse('summit-consultants', kwargs={'pk': summit.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == SummitAnketForSelectSerializer(SummitAnket.objects.order_by('-id'), many=True).data

    def test_add_consultant_supervisor(self, api_client, summit, user_factory, summit_anket_factory):
        url = reverse('summit-add-consultant', kwargs={'pk': summit.id})
        user = user_factory()
        summit_anket_factory(user=user, role=SummitAnket.SUPERVISOR, summit=summit)
        api_client.force_login(user=user)

        anket = summit_anket_factory(summit=summit)
        response = api_client.post(url, data={'anket_id': anket.id}, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {'summit_id': summit.id, 'consultant_id': anket.id, 'action': 'added'}
        assert SummitAnket.objects.get(id=anket.id).role == SummitAnket.CONSULTANT

    def test_add_consultant_consultant(self, api_login_client, summit, user_factory, summit_anket_factory):
        url = reverse('summit-add-consultant', kwargs={'pk': summit.id})
        user = user_factory()
        summit_anket_factory(user=user, role=SummitAnket.CONSULTANT, summit=summit)

        anket = summit_anket_factory(summit=summit)
        response = api_login_client.post(url, data={'anket_id': anket.id}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_consultant_to_other_summit(self, api_client, summit, summit_factory,
                                            user_factory, summit_anket_factory):
        url = reverse('summit-add-consultant', kwargs={'pk': summit.id})
        user = user_factory()
        summit_anket_factory(user=user, role=SummitAnket.SUPERVISOR, summit=summit)
        api_client.force_login(user=user)

        anket = summit_anket_factory(summit=summit_factory())
        response = api_client.post(url, data={'anket_id': anket.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_del_consultant_supervisor(self, api_client, summit, user_factory, summit_anket_factory):
        url = reverse('summit-del-consultant', kwargs={'pk': summit.id})
        user = user_factory()
        summit_anket_factory(user=user, role=SummitAnket.SUPERVISOR, summit=summit)
        api_client.force_login(user=user)

        anket = summit_anket_factory(summit=summit)
        response = api_client.post(url, data={'anket_id': anket.id}, format='json')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data == {'summit_id': summit.id, 'consultant_id': anket.id, 'action': 'removed'}
        assert SummitAnket.objects.get(id=anket.id).role == SummitAnket.VISITOR

    def test_del_consultant_consultant(self, api_login_client, summit, user_factory, summit_anket_factory):
        url = reverse('summit-del-consultant', kwargs={'pk': summit.id})
        user = user_factory()
        summit_anket_factory(user=user, role=SummitAnket.CONSULTANT, summit=summit)

        anket = summit_anket_factory(summit=summit)
        response = api_login_client.post(url, data={'anket_id': anket.id}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_del_consultant_to_other_summit(self, api_client, summit, summit_factory,
                                            user_factory, summit_anket_factory):
        url = reverse('summit-del-consultant', kwargs={'pk': summit.id})
        user = user_factory()
        summit_anket_factory(user=user, role=SummitAnket.SUPERVISOR, summit=summit)
        api_client.force_login(user=user)

        anket = summit_anket_factory(summit=summit_factory())
        response = api_client.post(url, data={'anket_id': anket.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
