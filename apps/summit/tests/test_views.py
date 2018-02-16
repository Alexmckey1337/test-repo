from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.db import IntegrityError
from django.db.models import OuterRef, Exists
from django.urls import reverse
from rest_framework import status

from apps.account.models import CustomUser
from apps.notification.backend import RedisBackend
from apps.payment.api.serializers import PaymentShowSerializer
from apps.summit.models import Summit, SummitLesson, SummitAnket, SummitTicket, AnketEmail
from apps.summit.regcode import encode_reg_code
from apps.summit.api.serializers import (
    SummitSerializer, SummitLessonSerializer, SummitAnketForSelectSerializer, SummitAnketNoteSerializer,
    SummitAnketForAppSerializer)
from apps.summit.api.views import SummitProfileListView, SummitStatisticsView, SummitBishopHighMasterListView, \
    SummitProfileViewSet, SummitTicketMakePrintedView, SummitTicketViewSet
from apps.summit.api.views_app import SummitProfileForAppViewSet, SummitProfileTreeForAppListView

BISHOP_LEVEL = 4


def get_queryset(s):
    emails = AnketEmail.objects.filter(anket=OuterRef('pk'), is_success=True)
    other_summits = SummitAnket.objects.filter(
        user_id=OuterRef('user_id'),
        summit__type_id=s.summit.type_id,
        summit__status=Summit.CLOSE
    )
    return s.summit.ankets.annotate(
        has_email=Exists(emails), has_achievement=Exists(other_summits)).select_related('status') \
        .base_queryset().annotate_total_sum().annotate_full_name().order_by(
        'user__last_name', 'user__first_name', 'user__middle_name')


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
        # summit_anket_factory.create_batch(10, user__master=master, summit=summit)
        for i in range(10):
            u = master.add_child(username='user{}'.format(i), master=master)
            summit_anket_factory(user=u, summit=summit)
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
        user = summit_anket_factory(summit=summit).user  # count: + 1, = 1, all_users_count: +1, = 1

        # count: + 3, = 4, all_users_count: +3, = 4
        for i in range(3):
            u = user.add_child(username='user{}'.format(i), master=user)
            summit_anket_factory(user=u, summit=summit, author=user)
        # count: + 1, = 5, all_users_count: +1, = 5
        second_level_user = user.add_child(username='user', master=user)
        summit_anket_factory(user=second_level_user, summit=summit, author=user)
        # count: + 8, = 13, all_users_count: +8, = 13
        for i in range(8):
            u = second_level_user.add_child(username='second_user{}'.format(i), master=second_level_user)
            summit_anket_factory(user=u, summit=summit, author=second_level_user)

        summit_anket_factory.create_batch(15, summit=summit)  # count: + 0, = 13, all_users_count: +15, = 28
        other_user = user_factory()  # count: + 0, = 13, all_users_count: +1, = 29
        summit_anket_factory(user=other_user, summit=summit, author=user_factory())
        # count: + 0, = 13, all_users_count: + 32, = 61
        for i in range(32):
            u = other_user.add_child(username='other_user{}'.format(i), master=other_user)
            summit_anket_factory(user=u, summit=summit, author=other_user)

        url = reverse('summit-profile-list', kwargs={'pk': summit.id})

        response = api_login_client.get(url, data={'author_tree': user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 13


@pytest.mark.django_db
class TestSummitProfileViewSet:
    def test_create_payment(self, api_client, creator, anket, currency_factory):
        url = reverse('summit_profiles-create-payment', kwargs={'pk': anket.id})

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
        url = reverse('summit_profiles-payments', kwargs={'pk': anket.id})

        api_client.force_login(viewer['anket'].user)
        api_login_client = api_client

        response = api_login_client.get(url, format='json')

        assert response.status_code == viewer['code']
        if viewer['code'] == status.HTTP_200_OK:
            assert response.data == PaymentShowSerializer(anket.payments.all(), many=True).data

    def test_create_note(self, api_login_client, anket):
        url = reverse('summit_profiles-create-note', kwargs={'pk': anket.id})

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
        url = reverse('summit_profiles-notes', kwargs={'pk': anket.id})

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

        url = reverse('summit_profiles-codes')

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

        url = reverse('summit_profiles-set-ticket-status', kwargs={'pk': profile.pk})

        response = api_client.post(url, data={'new_status': new_status}, format='json')
        profile.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert profile.ticket_status == new_status

    @pytest.mark.parametrize('new_status', map(lambda s: 'invalid{}'.format(s[0]), SummitAnket.TICKET_STATUSES))
    def test_set_ticket_status_with_invalid_new_status(
            self, monkeypatch, api_client, new_status, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory(ticket_status='none')

        url = reverse('summit_profiles-set-ticket-status', kwargs={'pk': profile.pk})

        response = api_client.post(url, data={'new_status': new_status}, format='json')
        profile.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert profile.ticket_status == 'none'

    def test_set_ticket_status_with_invalid_old_status(
            self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory(ticket_status='invalid')

        url = reverse('summit_profiles-set-ticket-status', kwargs={'pk': profile.pk})

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

        url = reverse('summit_profiles-set-ticket-status', kwargs={'pk': profile.pk})

        response = api_client.post(url, format='json')
        profile.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert profile.ticket_status == new_status

    def test_delete_without_payments(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)
        profile = summit_anket_factory()

        url = reverse('summit_profiles-detail', kwargs={'pk': profile.pk})

        response = api_client.delete(url, format='json')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_with_payments(self, monkeypatch, api_client, summit_anket_factory, payment_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory()
        payment_factory(purpose=profile)

        url = reverse('summit_profiles-detail', kwargs={'pk': profile.pk})
        response = api_client.delete(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_predelete_status(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)
        profile = summit_anket_factory()

        url = reverse('summit_profiles-predelete', kwargs={'pk': profile.pk})

        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_predelete_data(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)
        profile = summit_anket_factory()

        url = reverse('summit_profiles-predelete', kwargs={'pk': profile.pk})

        response = api_client.get(url, format='json')

        assert set(response.data.keys()) == {'notes', 'lessons', 'summits', 'users', 'consultants'}

    def test_partial_update_status_code(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory()

        url = reverse('summit_profiles-detail', kwargs={'pk': profile.pk})
        response = api_client.patch(url, data={'description': 'two'}, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_partial_update_data(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory(description='one')

        url = reverse('summit_profiles-detail', kwargs={'pk': profile.pk})
        api_client.patch(url, data={'description': 'two'}, format='json')
        profile.refresh_from_db()

        assert profile.description == 'two'

    def test_create_status_code(self, monkeypatch, api_client, user_factory, summit_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        user = user_factory()
        summit = summit_factory()

        url = reverse('summit_profiles-list')

        response = api_client.post(url, data={'user': user.id, 'summit': summit.id}, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_summit_code(self, monkeypatch, api_client, user_factory, summit_factory):
        monkeypatch.setattr(SummitProfileViewSet, 'check_permissions', lambda s, r: 0)

        user = user_factory()
        summit = summit_factory()

        url = reverse('summit_profiles-list')

        api_client.post(url, data={'user': user.id, 'summit': summit.id}, format='json')
        profile = SummitAnket.objects.order_by('pk').last()

        assert profile.code == '0{}'.format(4000000 + profile.id)


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
        # summit_anket_factory.create_batch(10, user__master=master, summit=summit)
        for i in range(10):
            u = master.add_child(username='master{}'.format(i), master=master)
            summit_anket_factory(user=u, summit=summit)
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
        user = summit_anket_factory(summit=summit).user  # count: + 1, = 1, all_users_count: +1, = 1

        # count: + 3, = 4, all_users_count: +3, = 4
        for i in range(3):
            u = user.add_child(username='user{}'.format(i), master=user)
            summit_anket_factory(user=u, summit=summit, author=user)
        # second_level_user = user_factory(master=user)  # count: + 1, = 5, all_users_count: +1, = 5
        second_level_user = user.add_child(username='secord_user', master=user)
        summit_anket_factory(user=second_level_user, summit=summit, author=user)
        # count: + 8, = 13, all_users_count: +8, = 13
        # summit_anket_factory.create_batch(8, user__master=second_level_user, summit=summit, author=second_level_user)
        for i in range(8):
            u = second_level_user.add_child(username='second_user{}'.format(i), master=second_level_user)
            summit_anket_factory(user=u, summit=summit, author=second_level_user)

        summit_anket_factory.create_batch(15, summit=summit)  # count: + 0, = 13, all_users_count: +15, = 28
        other_user = user_factory()  # count: + 0, = 13, all_users_count: +1, = 29
        summit_anket_factory(user=other_user, summit=summit, author=user_factory())
        # count: + 0, = 13, all_users_count: + 32, = 61
        for i in range(32):
            u = other_user.add_child(username='other_user{}'.format(i), master=other_user)
            summit_anket_factory(user=u, summit=summit, author=other_user)

        url = reverse('summit-stats', kwargs={'pk': summit.id})

        response = api_login_client.get(url, data={'author_tree': user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 13

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


@pytest.mark.django_db
class TestSummitProfileForAppViewSet:
    def test_by_reg_code_status_code(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory()
        r = RedisBackend()
        r.delete(profile.reg_code)

        url = '/api/app/users/by_reg_code/?reg_code={}'.format(profile.reg_code)
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_by_reg_code_profile_status_exist(
            self, monkeypatch, api_client, summit_anket_factory, profile_status_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory()
        profile_status = profile_status_factory(
            anket=profile, reg_code_requested=False, reg_code_requested_date=datetime(2000, 2, 4))
        r = RedisBackend()
        r.delete(profile.reg_code)

        url = '/api/app/users/by_reg_code/?reg_code={}'.format(profile.reg_code)
        response = api_client.get(url, format='json')

        profile_status.refresh_from_db()
        assert response.data == SummitAnketForAppSerializer(profile).data
        assert not profile_status.reg_code_requested
        assert profile_status.reg_code_requested_date == datetime(2000, 2, 4)

    def test_by_reg_code_profile_status_not_exist(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory()
        r = RedisBackend()
        r.delete(profile.reg_code)
        assert not hasattr(profile, 'status')

        url = '/api/app/users/by_reg_code/?reg_code={}'.format(profile.reg_code)
        response = api_client.get(url, format='json')
        profile = SummitAnket.objects.get(pk=profile.id)

        assert hasattr(profile, 'status')
        assert response.data == SummitAnketForAppSerializer(profile).data
        assert profile.status.reg_code_requested

    def test_by_reg_code_without_reg_code(self, monkeypatch, api_client):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        url = '/api/app/users/by_reg_code/'
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_by_reg_code_invalid_format(self, monkeypatch, api_client):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        url = '/api/app/users/by_reg_code/?reg_code=invalid'
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_by_reg_code_profile_not_exist(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory()
        profile_id = profile.id
        profile.delete()

        url = '/api/app/users/by_reg_code/?reg_code={}'.format(encode_reg_code(profile_id))
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_by_reg_code_invalid_reg_code(self, monkeypatch, api_client, summit_anket_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        profile = summit_anket_factory()

        code = encode_reg_code(profile.id)
        code = str(int('0x' + code, 0) + 1)

        url = '/api/app/users/by_reg_code/?reg_code={}'.format(code)
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_by_reg_date_status_code(self, monkeypatch, api_client):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        url = '/api/app/users/by_reg_date/'
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_by_reg_date_without_date(self, monkeypatch, api_client, summit_anket_factory, profile_status_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        day = datetime.now() - timedelta(days=1)
        early = day - timedelta(days=1)
        later = day + timedelta(days=1)

        early_profile = summit_anket_factory()
        profile = summit_anket_factory()
        later_profile = summit_anket_factory()
        profile_status_factory(anket=early_profile, reg_code_requested_date=early)
        profile_status_factory(anket=profile, reg_code_requested_date=day)
        profile_status_factory(anket=later_profile, reg_code_requested_date=later)

        url = '/api/app/users/by_reg_date/'
        response = api_client.get(url, format='json')

        assert set(p['visitor_id'] for p in response.data) == {profile.id}

    @pytest.mark.xfail
    def test_by_reg_date_without_to_date(self, monkeypatch, api_client, summit_anket_factory, profile_status_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        day = datetime.now()
        early = day - timedelta(days=1)
        later = day + timedelta(days=1)

        early_profile = summit_anket_factory()
        profile = summit_anket_factory()
        later_profile = summit_anket_factory()
        profile_status_factory(anket=early_profile, reg_code_requested_date=early)
        profile_status_factory(anket=profile, reg_code_requested_date=day)
        profile_status_factory(anket=later_profile, reg_code_requested_date=later)

        url = '/api/app/users/by_reg_date/?from_date={}'.format(day.strftime("%Y-%m-%d"))
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert set(p['visitor_id'] for p in response.data) == {profile.id, later_profile.id}

    @pytest.mark.xfail
    def test_by_reg_date_without_from_date(self, monkeypatch, api_client, summit_anket_factory, profile_status_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        day = datetime(2000, 2, 4)
        early = day - timedelta(days=1)
        later = day + timedelta(days=1)

        early_profile = summit_anket_factory()
        profile = summit_anket_factory()
        later_profile = summit_anket_factory()
        profile_status_factory(anket=early_profile, reg_code_requested_date=early)
        profile_status_factory(anket=profile, reg_code_requested_date=day)
        profile_status_factory(anket=later_profile, reg_code_requested_date=later)

        url = '/api/app/users/by_reg_date/?to_date={}'.format(day.strftime("%Y-%m-%d"))
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert set(p['visitor_id'] for p in response.data) == {early_profile.id, profile.id}

    def test_by_reg_date_from_date_eq_to_date(
            self, monkeypatch, api_client, summit_anket_factory, profile_status_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        day = datetime(2000, 2, 4)
        early = day - timedelta(days=1)
        later = day + timedelta(days=1)

        early_profile = summit_anket_factory()
        profile = summit_anket_factory()
        later_profile = summit_anket_factory()
        profile_status_factory(anket=early_profile, reg_code_requested_date=early)
        profile_status_factory(anket=profile, reg_code_requested_date=day)
        profile_status_factory(anket=later_profile, reg_code_requested_date=later)

        url = '/api/app/users/by_reg_date/?from_date={day}&to_date={day}'.format(day=day.strftime("%Y-%m-%d"))
        response = api_client.get(url, format='json')

        assert set(p['visitor_id'] for p in response.data) == {profile.id}

    def test_by_reg_date_from_date_gt_to_date(self, monkeypatch, api_client):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        url = '/api/app/users/by_reg_date/?from_date=2000-02-22&to_date=1999-12-22'
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_by_reg_date_from_date_lt_to_date(
            self, monkeypatch, api_client, summit_anket_factory, profile_status_factory):
        monkeypatch.setattr(SummitProfileForAppViewSet, 'check_permissions', lambda s, r: 0)

        day = datetime(2000, 2, 4)
        early = day - timedelta(days=1)
        later = day + timedelta(days=1)
        more_early = day - timedelta(days=2)
        more_later = day + timedelta(days=2)

        early_profile = summit_anket_factory()
        profile = summit_anket_factory()
        later_profile = summit_anket_factory()
        profile_status_factory(reg_code_requested_date=more_early)
        profile_status_factory(anket=early_profile, reg_code_requested_date=early)
        profile_status_factory(anket=profile, reg_code_requested_date=day)
        profile_status_factory(anket=later_profile, reg_code_requested_date=later)
        profile_status_factory(reg_code_requested_date=more_later)

        url = '/api/app/users/by_reg_date/?from_date={early}&to_date={later}'.format(
            early=early.strftime("%Y-%m-%d"), later=later.strftime("%Y-%m-%d"))
        response = api_client.get(url, format='json')

        assert set(p['visitor_id'] for p in response.data) == {early_profile.id, profile.id, later_profile.id}


@pytest.mark.django_db
class TestSummitProfileTreeForAppListView:
    def test_locations_without_date_time_and_interval(
            self, monkeypatch, api_client, summit_factory, visitor_location_factory):
        monkeypatch.setattr(SummitProfileTreeForAppListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(
            SummitProfileTreeForAppListView, 'get_queryset', lambda s: s.annotate_queryset(s.summit.ankets.all()))
        now = datetime.now()

        summit = summit_factory()
        early_location = visitor_location_factory(visitor__summit=summit, date_time=now - timedelta(minutes=11))
        location = visitor_location_factory(visitor__summit=summit, date_time=now - timedelta(minutes=9))

        url = '/api/app/summits/{}/users/'.format(summit.id)
        response = api_client.get(url, format='json')
        assert {p['id']: p['visitor_locations']['date_time'].date() if p['visitor_locations'] else None
                for p in response.data['profiles']} == {
                   location.visitor_id: now.date(), early_location.visitor_id: None}

    def test_locations_with_date_time(
            self, monkeypatch, api_client, summit_factory, visitor_location_factory):
        monkeypatch.setattr(SummitProfileTreeForAppListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(
            SummitProfileTreeForAppListView, 'get_queryset', lambda s: s.annotate_queryset(s.summit.ankets.all()))
        date_time = datetime(2000, 2, 24, 11, 33, 55)

        summit = summit_factory()
        early_location = visitor_location_factory(visitor__summit=summit, date_time=date_time - timedelta(minutes=6))
        less_location = visitor_location_factory(visitor__summit=summit, date_time=date_time - timedelta(minutes=4))
        more_location = visitor_location_factory(visitor__summit=summit, date_time=date_time + timedelta(minutes=4))
        later_location = visitor_location_factory(visitor__summit=summit, date_time=date_time + timedelta(minutes=6))

        url = '/api/app/summits/{}/users/?date_time=2000-02-24T11:33:55'.format(summit.id)
        response = api_client.get(url, format='json')
        assert {p['id']: p['visitor_locations']['date_time'].date() if p['visitor_locations'] else None
                for p in response.data['profiles']} == {
                   less_location.visitor_id: (date_time + timedelta(minutes=4)).date(),
                   more_location.visitor_id: (date_time - timedelta(minutes=4)).date(),
                   early_location.visitor_id: None,
                   later_location.visitor_id: None,
               }

    def test_locations_with_interval(
            self, monkeypatch, api_client, summit_factory, visitor_location_factory):
        monkeypatch.setattr(SummitProfileTreeForAppListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(
            SummitProfileTreeForAppListView, 'get_queryset', lambda s: s.annotate_queryset(s.summit.ankets.all()))
        now = datetime.now()

        summit = summit_factory()
        early_location = visitor_location_factory(visitor__summit=summit, date_time=now - timedelta(minutes=17))
        location = visitor_location_factory(visitor__summit=summit, date_time=now - timedelta(minutes=15))

        url = '/api/app/summits/{}/users/?interval=8'.format(summit.id)
        response = api_client.get(url, format='json')
        assert {p['id']: p['visitor_locations']['date_time'].date() if p['visitor_locations'] else None
                for p in response.data['profiles']} == {
                   location.visitor_id: now.date(), early_location.visitor_id: None}

    def test_locations_with_date_time_and_interval(
            self, monkeypatch, api_client, summit_factory, visitor_location_factory):
        monkeypatch.setattr(SummitProfileTreeForAppListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(
            SummitProfileTreeForAppListView, 'get_queryset', lambda s: s.annotate_queryset(s.summit.ankets.all()))
        date_time = datetime(2000, 2, 24, 11, 33, 55)

        summit = summit_factory()
        early_location = visitor_location_factory(visitor__summit=summit, date_time=date_time - timedelta(minutes=9))
        less_location = visitor_location_factory(visitor__summit=summit, date_time=date_time - timedelta(minutes=7))
        more_location = visitor_location_factory(visitor__summit=summit, date_time=date_time + timedelta(minutes=7))
        later_location = visitor_location_factory(visitor__summit=summit, date_time=date_time + timedelta(minutes=9))

        url = '/api/app/summits/{}/users/?date_time=2000-02-24T11:33:55&interval=8'.format(summit.id)
        response = api_client.get(url, format='json')
        assert {p['id']: p['visitor_locations']['date_time'].date() if p['visitor_locations'] else None
                for p in response.data['profiles']} == {
                   less_location.visitor_id: (date_time + timedelta(minutes=4)).date(),
                   more_location.visitor_id: (date_time - timedelta(minutes=4)).date(),
                   early_location.visitor_id: None,
                   later_location.visitor_id: None,
               }

    def test_profiles_without_master_id_for_consultant_or_high(
            self, monkeypatch, api_client, summit_factory, user_factory, summit_anket_factory):
        monkeypatch.setattr(SummitProfileTreeForAppListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(CustomUser, 'is_summit_consultant_or_high', lambda s, a: True)

        summit = summit_factory()
        top_user = summit_anket_factory(summit=summit)
        # summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user', master=top_user.user)
        summit_anket_factory(user=u, summit=summit)

        user = user_factory()
        api_client.force_login(user=user)

        url = '/api/app/summits/{}/users/'.format(summit.id)
        response = api_client.get(url, format='json')
        assert {p['id'] for p in response.data['profiles']} == {top_user.id}

    def test_profiles_without_master_id_for_less_of_consultant(
            self, monkeypatch, api_client, summit_factory, summit_anket_factory):
        monkeypatch.setattr(SummitProfileTreeForAppListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(CustomUser, 'is_summit_consultant_or_high', lambda s, a: False)

        summit = summit_factory()
        top_user = summit_anket_factory(summit=summit)
        # profile = summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user', master=top_user.user)
        profile = summit_anket_factory(user=u, summit=summit)
        # summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user_other', master=top_user.user)
        summit_anket_factory(user=u, summit=summit)
        # profile_child = summit_anket_factory.create_batch(2, summit=summit, user__master=profile.user)
        profile_child = []
        for i in range(2):
            u = profile.user.add_child(username='profile_user{}'.format(i), master=profile.user)
            profile_child.append(summit_anket_factory(user=u, summit=summit))

        api_client.force_login(user=profile.user)

        url = '/api/app/summits/{}/users/'.format(summit.id)
        response = api_client.get(url, format='json')
        assert {p['id'] for p in response.data['profiles']} == {p.id for p in profile_child}

    def test_profiles_with_master_id_for_consultant_or_high(
            self, monkeypatch, api_client, summit_factory, summit_anket_factory):
        monkeypatch.setattr(SummitProfileTreeForAppListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(CustomUser, 'is_summit_consultant_or_high', lambda s, a: True)

        summit = summit_factory()
        top_user = summit_anket_factory(summit=summit)
        # profile = summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user', master=top_user.user)
        profile = summit_anket_factory(user=u, summit=summit)
        # master = summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user_other', master=top_user.user)
        master = summit_anket_factory(user=u, summit=summit)
        # summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user_again', master=top_user.user)
        summit_anket_factory(user=u, summit=summit)
        # summit_anket_factory.create_batch(2, summit=summit, user__master=profile.user)
        for i in range(2):
            u = profile.user.add_child(username='profile{}'.format(i), master=profile.user)
            summit_anket_factory(user=u, summit=summit)
        # master_child = summit_anket_factory.create_batch(2, summit=summit, user__master=master.user)
        master_child = []
        for i in range(2):
            u = master.user.add_child(username='master{}'.format(i), master=master.user)
            master_child.append(summit_anket_factory(user=u, summit=summit))

        api_client.force_login(user=profile.user)

        url = '/api/app/summits/{}/users/{}/'.format(summit.id, master.user.id)
        response = api_client.get(url, format='json')
        assert {p['id'] for p in response.data['profiles']} == {p.id for p in master_child}

    def test_profiles_with_master_id_for_less_of_consultant(
            self, monkeypatch, api_client, summit_factory, summit_anket_factory):
        monkeypatch.setattr(SummitProfileTreeForAppListView, 'check_permissions', lambda s, r: 0)
        monkeypatch.setattr(CustomUser, 'is_summit_consultant_or_high', lambda s, a: False)

        summit = summit_factory()
        top_user = summit_anket_factory(summit=summit)
        # profile = summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user', master=top_user.user)
        profile = summit_anket_factory(user=u, summit=summit)
        # master = summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user_other', master=top_user.user)
        master = summit_anket_factory(user=u, summit=summit)
        # summit_anket_factory(summit=summit, user__master=top_user.user)
        u = top_user.user.add_child(username='top_user_again', master=top_user.user)
        summit_anket_factory(user=u, summit=summit)
        # summit_anket_factory.create_batch(2, summit=summit, user__master=profile.user)
        for i in range(2):
            u = profile.user.add_child(username='profile{}'.format(i), master=profile.user)
            summit_anket_factory(user=u, summit=summit)
        # master_child = summit_anket_factory.create_batch(2, summit=summit, user__master=master.user)
        master_child = []
        for i in range(2):
            u = master.user.add_child(username='master{}'.format(i), master=master.user)
            master_child.append(summit_anket_factory(user=u, summit=summit))

        api_client.force_login(user=profile.user)

        url = '/api/app/summits/{}/users/{}/'.format(summit.id, master.user.id)
        response = api_client.get(url, format='json')
        assert {p['id'] for p in response.data['profiles']} == {p.id for p in master_child}

    def test_users_without_code(self, monkeypatch, api_client, summit_ticket_factory, summit_anket_factory):
        monkeypatch.setattr(SummitTicketViewSet, 'check_permissions', lambda s, r: 0)

        ticket = summit_ticket_factory()
        summit_anket_factory()
        ticket_profiles = summit_anket_factory.create_batch(2)
        ticket.users.set((p.id for p in ticket_profiles))

        url = '/api/summit_tickets/{}/users/'.format(ticket.id)
        response = api_client.get(url, format='json')

        assert len(response.data) == 2
        assert {u['is_active'] for u in response.data} == {False}

    def test_users_with_code(self, monkeypatch, api_client, summit_ticket_factory, summit_anket_factory):
        monkeypatch.setattr(SummitTicketViewSet, 'check_permissions', lambda s, r: 0)

        ticket = summit_ticket_factory()
        summit_anket_factory.create_batch(4)
        ticket_profiles = summit_anket_factory.create_batch(2)
        code_profile = summit_anket_factory(code='22222')
        ticket.users.set((p.id for p in ticket_profiles + [code_profile]))

        url = '/api/summit_tickets/{}/users/?code=22222'.format(ticket.id)
        response = api_client.get(url, format='json')

        assert len(response.data) == 3
        assert {u['is_active'] for u in response.data if u['code'] != '22222'} == {False}
        assert [u['is_active'] for u in response.data if u['code'] == '22222'] == [True]


@pytest.mark.xfail
@pytest.mark.django_db
class TestSummitReportByBishops:
    def test_dont_can_see_report(self):
        assert False

    def test_without_date(self):
        assert False

    def test_with_date(self):
        assert False

    def test_search_by_fio(self):
        assert False

    def test_filter_by_department(self):
        assert False


@pytest.mark.xfail
@pytest.mark.django_db
class TestGenerateSummitTickets:
    def test_with_users_without_image(self):
        assert False

    def test_without_new_profiles(self):
        assert False

    def test_ticket_users(self):
        assert False

    def test_creating_ticket(self):
        assert False

    def test_ticket_status_of_ticket_users(self):
        assert False
