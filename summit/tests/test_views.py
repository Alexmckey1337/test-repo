from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status, serializers

from payment.serializers import PaymentShowSerializer
from summit.models import Summit, SummitLesson, SummitAnket, SummitTicket
from summit.serializers import (
    SummitSerializer, SummitLessonSerializer, SummitAnketForSelectSerializer, SummitAnketNoteSerializer)
from summit.views import SummitProfileListView, SummitStatisticsView, SummitBishopHighMasterListView, \
    SummitProfileViewSet, SummitTicketMakePrintedView

BISHOP_LEVEL = 4


def get_queryset(s):
    return SummitAnket.objects.base_queryset().annotate_total_sum().annotate_full_name().filter(summit_id=s.summit)


def get_stats_queryset(self):
    qs = self.annotate_queryset(self.summit.ankets)
    return qs


def save_db_error(self, *args, **kwargs):
    raise IntegrityError()


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
class TestSummitProfileListView:
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


@pytest.mark.django_db
class TestSummitProfileViewSet:
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

    def test_codes(self, monkeypatch, api_client, summit_factory, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        summit = summit_factory()
        other_summit = summit_factory()
        profiles = summit_anket_factory.create_batch(2, summit=summit)
        summit_anket_factory.create_batch(4, summit=other_summit)

        url = reverse('summit_ankets-codes')

        response = api_client.get('{}?summit_id={}'.format(url, summit.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['ticket_count'] == len(profiles)
        assert set(map(
            lambda p: p['code'],
            response.data['ticket_codes'])) == set(map(lambda p: p.code, profiles))

    @pytest.mark.parametrize('new_status', map(lambda s: s[0], SummitAnket.TICKET_STATUSES))
    def test_set_ticket_status_with_new_status(
            self, monkeypatch, api_client, new_status, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory(ticket_status='none')

        url = reverse('summit_ankets-set-ticket-status', kwargs={'pk': profile.pk})

        response = api_client.post(url, data={'new_status': new_status}, format='json')
        profile.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert profile.ticket_status == new_status

    @pytest.mark.parametrize('new_status', map(lambda s: 'invalid{}'.format(s[0]), SummitAnket.TICKET_STATUSES))
    def test_set_ticket_status_with_invalid_new_status(
            self, monkeypatch, api_client, new_status, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory(ticket_status='none')

        url = reverse('summit_ankets-set-ticket-status', kwargs={'pk': profile.pk})

        response = api_client.post(url, data={'new_status': new_status}, format='json')
        profile.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert profile.ticket_status == 'none'

    def test_set_ticket_status_with_invalid_old_status(
            self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory(ticket_status='invalid')

        url = reverse('summit_ankets-set-ticket-status', kwargs={'pk': profile.pk})

        response = api_client.post(url, format='json')
        profile.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert profile.ticket_status == 'invalid'

    @pytest.mark.parametrize('old_status,new_status', settings.NEW_TICKET_STATUS.items(),
                             ids=tuple(map(lambda s: '{}->{}'.format(*s), settings.NEW_TICKET_STATUS.items())))
    def test_set_ticket_status_without_new_status(
            self, monkeypatch, api_client, old_status, new_status, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory(ticket_status=old_status)

        url = reverse('summit_ankets-set-ticket-status', kwargs={'pk': profile.pk})

        response = api_client.post(url, format='json')
        profile.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert profile.ticket_status == new_status

    @pytest.mark.hh
    def test_delete_without_payments(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)
        profile = summit_anket_factory()

        url = reverse('summit_ankets-detail', kwargs={'pk': profile.pk})

        response = api_client.delete(url, format='json')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.hh
    def test_delete_with_payments(self, monkeypatch, api_client, summit_anket_factory, payment_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory()
        payment_factory(purpose=profile)

        url = reverse('summit_ankets-detail', kwargs={'pk': profile.pk})
        response = api_client.delete(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.hh
    def test_predelete_status(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)
        profile = summit_anket_factory()

        url = reverse('summit_ankets-predelete', kwargs={'pk': profile.pk})

        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.hh
    def test_predelete_data(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)
        profile = summit_anket_factory()

        url = reverse('summit_ankets-predelete', kwargs={'pk': profile.pk})

        response = api_client.get(url, format='json')

        assert set(response.data.keys()) == {'notes', 'lessons', 'summits', 'users', 'consultants'}


@pytest.mark.django_db
class TestSummitTicketMakePrintedView:
    def test_status(self, monkeypatch, api_client, summit_ticket_factory):
        monkeypatch.setattr(SummitTicketMakePrintedView, 'check_permissions', lambda s, r: 0)

        ticket = summit_ticket_factory()

        url = reverse('summit-ticket-print', kwargs={'ticket': ticket.pk})
        response = api_client.post(url, format='json')
        ticket.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK

    def test_summit_ticket(self, monkeypatch, api_client, summit_ticket_factory):
        monkeypatch.setattr(SummitTicketMakePrintedView, 'check_permissions', lambda s, r: 0)

        ticket = summit_ticket_factory()

        url = reverse('summit-ticket-print', kwargs={'ticket': ticket.pk})
        api_client.post(url, format='json')
        ticket.refresh_from_db()

        assert ticket.is_printed

    @pytest.mark.parametrize('ticket_status', map(lambda s: s[0], SummitAnket.TICKET_STATUSES))
    def test_summit_ticket_users(
            self, monkeypatch, api_client, summit_ticket_factory, summit_anket_factory, ticket_status):
        monkeypatch.setattr(SummitTicketMakePrintedView, 'check_permissions', lambda s, r: 0)

        ticket = summit_ticket_factory()
        profiles = summit_anket_factory.create_batch(2, ticket_status=ticket_status)
        ticket.users.set([p.id for p in profiles])

        url = reverse('summit-ticket-print', kwargs={'ticket': ticket.pk})
        api_client.post(url, format='json')

        if ticket_status == SummitAnket.GIVEN:
            assert set(ticket.users.values_list('ticket_status', flat=True)) == {SummitAnket.GIVEN}
        else:
            assert set(ticket.users.values_list('ticket_status', flat=True)) == {SummitAnket.PRINTED}

    def test_status_with_db_error(self, monkeypatch, api_client, summit_ticket_factory):
        monkeypatch.setattr(SummitTicketMakePrintedView, 'check_permissions', lambda s, r: 0)

        ticket = summit_ticket_factory()

        url = reverse('summit-ticket-print', kwargs={'ticket': ticket.pk})
        monkeypatch.setattr(SummitTicket, 'save', save_db_error)
        response = api_client.post(url, format='json')
        ticket.refresh_from_db()

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_summit_ticket_db_error(self, monkeypatch, api_client, summit_ticket_factory):
        monkeypatch.setattr(SummitTicketMakePrintedView, 'check_permissions', lambda s, r: 0)

        ticket = summit_ticket_factory()

        url = reverse('summit-ticket-print', kwargs={'ticket': ticket.pk})
        monkeypatch.setattr(SummitTicket, 'save', save_db_error)
        api_client.post(url, format='json')
        ticket.refresh_from_db()

        assert not ticket.is_printed

    @pytest.mark.parametrize('ticket_status', map(lambda s: s[0], SummitAnket.TICKET_STATUSES))
    def test_summit_ticket_users_db_error(
            self, monkeypatch, api_client, summit_ticket_factory, summit_anket_factory, ticket_status):
        monkeypatch.setattr(SummitTicketMakePrintedView, 'check_permissions', lambda s, r: 0)

        ticket = summit_ticket_factory()
        profiles = summit_anket_factory.create_batch(2, ticket_status=ticket_status)
        ticket.users.set([p.id for p in profiles])

        url = reverse('summit-ticket-print', kwargs={'ticket': ticket.pk})
        monkeypatch.setattr(SummitTicket, 'save', save_db_error)
        api_client.post(url, format='json')

        assert set(ticket.users.values_list('ticket_status', flat=True)) == {ticket_status}


@pytest.mark.django_db
def test_app_request_count(api_client, summit_factory, profile_status_factory):
    summit = summit_factory()
    other_summit = summit_factory()

    profile_status_factory(anket__summit=other_summit, reg_code_requested=False)
    profile_status_factory.create_batch(2, anket__summit=other_summit, reg_code_requested=True)
    profile_status_factory.create_batch(4, anket__summit=summit, reg_code_requested=False)
    profile_status_factory.create_batch(8, anket__summit=summit, reg_code_requested=True)

    url = reverse('summit-app-profile-list', kwargs={'summit_id': summit.id})

    response = api_client.get(url, format='json')

    assert response.data == {'total': 12, 'requested': 8}


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

    def test_filter_by_date_with_date(
            self, monkeypatch, api_client, summit_attend_factory, summit_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        monkeypatch.setattr(SummitStatisticsView, 'pagination_class', None)
        now = datetime.now()
        summit = summit_factory()

        summit_attend_factory.create_batch(10, anket__summit=summit, date=now)
        summit_attend_factory.create_batch(8, anket__summit=summit, date=(now - timedelta(days=2)))

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_client.get(
            '{}?date={}'.format(url, now.strftime('%Y-%m-%d')), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(list(filter(lambda p: p['attended'], response.data))) == 10

    def test_filter_by_date_without_date(
            self, monkeypatch, api_client, summit_attend_factory, summit_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(SummitStatisticsView, 'get_queryset', get_stats_queryset)
        monkeypatch.setattr(SummitStatisticsView, 'pagination_class', None)
        now = datetime.now()
        summit = summit_factory()

        summit_attend_factory.create_batch(10, anket__summit=summit, date=now)
        summit_attend_factory.create_batch(8, anket__summit=summit, date=(now - timedelta(days=2)))

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(list(filter(lambda p: p['attended'], response.data))) == 10

    def test_filter_by_date_with_invalid_date(
            self, monkeypatch, api_client, summit_factory):
        monkeypatch.setattr(SummitStatisticsView, 'check_permissions', lambda s, r: 0)
        summit = summit_factory()

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_client.get('{}?date={}'.format(url, '01.01.2017'), format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSummitBishopHighMasterListView:
    def test_filter_with_correct_summit(self, monkeypatch, api_client, summit_factory, summit_anket_factory):
        monkeypatch.setattr(SummitBishopHighMasterListView, 'check_permissions', lambda s, r: 0)

        summit = summit_factory()
        summit_anket_factory(user__hierarchy__level=22, summit=summit)

        url = reverse('summit-masters', kwargs={'pk': summit.id})

        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_with_incorrect_summit(self, monkeypatch, api_client, summit_factory, summit_anket_factory):
        monkeypatch.setattr(SummitBishopHighMasterListView, 'check_permissions', lambda s, r: 0)

        summit = summit_factory()
        summit_anket_factory(user__hierarchy__level=22, summit=summit)

        other_summit = summit_factory()

        url = reverse('summit-masters', kwargs={'pk': other_summit.id})

        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    @pytest.mark.parametrize('h', range(11))
    def test_filter_with_correct_hierarchy(self, monkeypatch, api_client, summit_anket_factory, h):
        monkeypatch.setattr(SummitBishopHighMasterListView, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory(user__hierarchy__level=h)

        url = reverse('summit-masters', kwargs={'pk': profile.summit.id})

        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == (1 if h >= BISHOP_LEVEL else 0)
