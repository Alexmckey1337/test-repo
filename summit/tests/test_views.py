from decimal import Decimal

import pytest
from django.db.models import OuterRef, Exists
from django.urls import reverse
from rest_framework import status

from payment.serializers import PaymentShowSerializer
from summit.models import Summit, SummitLesson, SummitAnket, SummitAttend
from summit.serializers import (
    SummitSerializer, SummitLessonSerializer, SummitAnketForSelectSerializer, SummitAnketNoteSerializer)
from summit.views import SummitProfileListView, SummitStatisticsView


def get_queryset(s):
    return SummitAnket.objects.base_queryset().annotate_total_sum().annotate_full_name().filter(summit_id=s.summit)


def get_stats_queryset(self):
    subqs = SummitAttend.objects.filter(date=self.filter_date, anket=OuterRef('pk'))
    qs = self.summit.ankets.select_related('user').annotate(attended=Exists(subqs)).annotate_full_name().order_by(
        'user__last_name', 'user__first_name', 'user__middle_name')
    return qs


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


@pytest.mark.django_db
class TestSummitAnketTableViewSet:
    def test_create_payment(self, api_client, creator, anket, currency_factory):
        url = reverse('summit_ankets-create-payment', kwargs={'pk': anket.id})

        api_client.force_login(creator['anket'].user)
        api_login_client = api_client

        data = {
            'sum': '10',
            'description': 'no desc',
            'rate': '1.22',
            'currency': currency_factory().id,
        }
        response = api_login_client.post(url, data=data, format='json')

        assert response.status_code == creator['code']

        if creator['code'] == status.HTTP_201_CREATED:
            payment = anket.payments.get()
            assert payment.sum == Decimal(data['sum'])
            assert payment.rate == Decimal(data['rate'])
            assert payment.description == data['description']
            assert payment.currency_sum_id == data['currency']
            assert response.data == PaymentShowSerializer(payment).data

    def test_payments(self, api_client, viewer, anket, payment_factory):
        payment_factory.create_batch(6, purpose=anket)
        url = reverse('summit_ankets-payments', kwargs={'pk': anket.id})

        api_client.force_login(viewer['anket'].user)
        api_login_client = api_client

        response = api_login_client.get(url, format='json')

        assert response.status_code == viewer['code']
        if viewer['code'] == status.HTTP_200_OK:
            assert response.data == PaymentShowSerializer(anket.payments.all(), many=True).data

    def test_create_note(self, api_login_client, anket):
        url = reverse('summit_ankets-create-note', kwargs={'pk': anket.id})

        data = {
            'text': 'very long text',
        }
        response = api_login_client.post(url, data=data, format='json')

        note = anket.notes.get()

        assert response.status_code == status.HTTP_201_CREATED
        assert note.text == data['text']
        assert response.data == SummitAnketNoteSerializer(note).data

    def test_notes(self, api_client, summit_anket_factory, anket, anket_note_factory):
        anket_note_factory.create_batch(6)
        consultant_anket = summit_anket_factory(summit=anket.summit, role=SummitAnket.CONSULTANT)
        url = reverse('summit_ankets-notes', kwargs={'pk': anket.id})

        api_client.force_login(consultant_anket.user)
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == SummitAnketNoteSerializer(anket.notes.all(), many=True).data

    @pytest.mark.parametrize(
        'role,count', [
            (SummitAnket.SUPERVISOR, 5),
            (SummitAnket.CONSULTANT, 5),
            (SummitAnket.VISITOR, 0),
        ], ids=['supervisor', 'consultant', 'visitor'])
    def test_filter_ankets_by_current_user(
            self, monkeypatch, api_client, user_factory, summit_factory, summit_anket_factory, role, count):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        user = user_factory()

        summit = summit_factory()
        summit_anket_factory.create_batch(4, summit=summit)
        summit_anket_factory(user=user, summit=summit, role=role)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})
        api_client.force_login(user)

        response = api_client.get(url, format='json')

        assert len(response.data['results']) == count

    def test_user_search_by_fio(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory(user__last_name='searchlast', user__first_name='searchfirst', summit=summit)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_fio={}'.format(url, 'searchfirst searchlast'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_user_search_by_email(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory(user__email='mysupermail@test.com', summit=summit)
        summit_anket_factory(user__email='test@mysupermail.com', summit=summit)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_email={}'.format(url, 'mysupermail'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_phone(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory(user__phone_number='+380990002246', summit=summit)
        summit_anket_factory(user__phone_number='+380992299000', summit=summit)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_phone_number={}'.format(url, '99000'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_country(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory.create_batch(8, user__country='Ukraine', summit=summit)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_country={}'.format(url, 'Ukraine'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_user_search_by_city(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory.create_batch(8, user__city='Tokio', summit=summit)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_city={}'.format(url, 'Tokio'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_user_list_filter_by_hierarchy(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, hierarchy_factory):
        other_hierarchy = hierarchy_factory()
        hierarchy = hierarchy_factory()
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, user__hierarchy=hierarchy, summit=summit)
        summit_anket_factory.create_batch(20, user__hierarchy=other_hierarchy, summit=summit)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?hierarchy={}'.format(url, hierarchy.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_department(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, department_factory):
        other_department = department_factory()
        department = department_factory()
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        profiles = summit_anket_factory.create_batch(10, summit=summit)
        for p in profiles:
            p.departments.set([department])
        profiles = summit_anket_factory.create_batch(20, summit=summit)
        for p in profiles:
            p.departments.set([other_department])

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?department={}'.format(url, department.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    @pytest.mark.parametrize('ticket_status,count', [('none', 2), ('download', 4), ('print', 8)],
                             ids=['none', 'download', 'print'])
    def test_user_list_filter_by_ticket_status(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, ticket_status, count):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)

        summit = summit_factory()
        summit_anket_factory.create_batch(2, summit=summit, ticket_status='none')
        summit_anket_factory.create_batch(4, summit=summit, ticket_status='download')
        summit_anket_factory.create_batch(8, summit=summit, ticket_status='print')

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?ticket_status={}'.format(url, ticket_status), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == count

    @pytest.mark.parametrize('has_photo,count', [('true', 1), ('false', 2), ('all', 3)],
                             ids=['true', 'false', 'all'])
    def test_user_list_filter_by_has_photo(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, has_photo, count):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)

        summit = summit_factory()
        summit_anket_factory.create_batch(1, summit=summit, user__image='photo.jpg')
        summit_anket_factory.create_batch(2, summit=summit, user__image='')

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?has_photo={}'.format(url, has_photo), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == count

    def test_user_list_filter_by_master(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, user_factory):
        master = user_factory(username='master')
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, user__master=master, summit=summit)
        summit_anket_factory.create_batch(20, summit=summit)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?master={}'.format(url, master.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_master_tree(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory,
                                             user_factory):
        monkeypatch.setattr(SummitProfileListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitProfileListView, 'get_queryset', get_queryset)
        summit = summit_factory()
        user = user_factory()  # count: + 0, = 0, all_users_count: +1, = 1

        # count: + 3, = 3, all_users_count: +3, = 4
        summit_anket_factory.create_batch(3, user__master=user, summit=summit)
        second_level_user = user_factory(master=user)  # count: + 3, = 0, all_users_count: +1, = 5
        # count: + 8, = 11, all_users_count: +8, = 13
        summit_anket_factory.create_batch(8, user__master=second_level_user, summit=summit)

        summit_anket_factory.create_batch(15, summit=summit)  # count: + 0, = 11, all_users_count: +15, = 28
        other_user = user_factory()  # count: + 0, = 11, all_users_count: +1, = 29
        # count: + 0, = 11, all_users_count: + 32, = 61
        summit_anket_factory.create_batch(32, user__master=other_user, summit=summit)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get(url, data={'master_tree': user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 11


@pytest.mark.hh
@pytest.mark.django_db
class TestSummitStatisticsView:
    @pytest.mark.parametrize(
        'role,count', [
            (SummitAnket.SUPERVISOR, 5),
            (SummitAnket.CONSULTANT, 5),
            (SummitAnket.VISITOR, 0),
        ], ids=['supervisor', 'consultant', 'visitor'])
    def test_filter_ankets_by_current_user(
            self, monkeypatch, api_client, user_factory, summit_factory, summit_anket_factory, role, count):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        user = user_factory()

        summit = summit_factory()
        summit_anket_factory.create_batch(4, summit=summit)
        summit_anket_factory(user=user, summit=summit, role=role)

        url = reverse('summit-stats', kwargs={'pk': summit.id})
        api_client.force_login(user)

        response = api_client.get(url, format='json')

        assert len(response.data['results']) == count

    def test_user_search_by_fio(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory(user__last_name='searchlast', user__first_name='searchfirst', summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_fio={}'.format(url, 'searchfirst searchlast'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_user_search_by_email(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory(user__email='mysupermail@test.com', summit=summit)
        summit_anket_factory(user__email='test@mysupermail.com', summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_email={}'.format(url, 'mysupermail'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_phone(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory(user__phone_number='+380990002246', summit=summit)
        summit_anket_factory(user__phone_number='+380992299000', summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_phone_number={}'.format(url, '99000'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_country(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory.create_batch(8, user__country='Ukraine', summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_country={}'.format(url, 'Ukraine'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_user_search_by_city(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, summit=summit)
        summit_anket_factory.create_batch(8, user__city='Tokio', summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get(
            '{}?search_city={}'.format(url, 'Tokio'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_user_list_filter_by_hierarchy(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, hierarchy_factory):
        other_hierarchy = hierarchy_factory()
        hierarchy = hierarchy_factory()
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, user__hierarchy=hierarchy, summit=summit)
        summit_anket_factory.create_batch(20, user__hierarchy=other_hierarchy, summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?hierarchy={}'.format(url, hierarchy.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_department(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, department_factory):
        other_department = department_factory()
        department = department_factory()
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        profiles = summit_anket_factory.create_batch(10, summit=summit)
        for p in profiles:
            p.departments.set([department])
        profiles = summit_anket_factory.create_batch(20, summit=summit)
        for p in profiles:
            p.departments.set([other_department])

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?department={}'.format(url, department.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    @pytest.mark.parametrize('ticket_status,count', [('none', 2), ('download', 4), ('print', 8)],
                             ids=['none', 'download', 'print'])
    def test_user_list_filter_by_ticket_status(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, ticket_status, count):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)

        summit = summit_factory()
        summit_anket_factory.create_batch(2, summit=summit, ticket_status='none')
        summit_anket_factory.create_batch(4, summit=summit, ticket_status='download')
        summit_anket_factory.create_batch(8, summit=summit, ticket_status='print')

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?ticket_status={}'.format(url, ticket_status), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == count

    @pytest.mark.parametrize('has_photo,count', [('true', 1), ('false', 2), ('all', 3)],
                             ids=['true', 'false', 'all'])
    def test_user_list_filter_by_has_photo(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, has_photo, count):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)

        summit = summit_factory()
        summit_anket_factory.create_batch(1, summit=summit, user__image='photo.jpg')
        summit_anket_factory.create_batch(2, summit=summit, user__image='')

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?has_photo={}'.format(url, has_photo), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == count

    @pytest.mark.parametrize('attended,count', [('true', 1), ('false', 2), ('all', 3)],
                             ids=['true', 'false', 'all'])
    def test_user_list_filter_by_attended(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_attend_factory,
            summit_factory, attended, count):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)

        summit = summit_factory()
        summit_attend_factory.create_batch(1, anket__summit=summit)
        summit_anket_factory.create_batch(2, summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?attended={}'.format(url, attended), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == count

    def test_user_list_filter_by_master(
            self, monkeypatch, api_login_client, summit_anket_factory, summit_factory, user_factory):
        master = user_factory(username='master')
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        summit_anket_factory.create_batch(10, user__master=master, summit=summit)
        summit_anket_factory.create_batch(20, summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get('{}?master={}'.format(url, master.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_master_tree(self, monkeypatch, api_login_client, summit_anket_factory, summit_factory,
                                             user_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        summit = summit_factory()
        user = user_factory()  # count: + 0, = 0, all_users_count: +1, = 1

        # count: + 3, = 3, all_users_count: +3, = 4
        summit_anket_factory.create_batch(3, user__master=user, summit=summit)
        second_level_user = user_factory(master=user)  # count: + 3, = 0, all_users_count: +1, = 5
        # count: + 8, = 11, all_users_count: +8, = 13
        summit_anket_factory.create_batch(8, user__master=second_level_user, summit=summit)

        summit_anket_factory.create_batch(15, summit=summit)  # count: + 0, = 11, all_users_count: +15, = 28
        other_user = user_factory()  # count: + 0, = 11, all_users_count: +1, = 29
        # count: + 0, = 11, all_users_count: + 32, = 61
        summit_anket_factory.create_batch(32, user__master=other_user, summit=summit)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get(url, data={'master_tree': user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 11
