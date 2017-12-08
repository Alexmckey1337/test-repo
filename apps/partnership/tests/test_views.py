# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta, date
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status, permissions

from apps.partnership.models import Partnership, Deal
from apps.partnership.api.serializers import DealSerializer, DealCreateSerializer, DealUpdateSerializer
from apps.partnership.api.views import PartnershipViewSet
from apps.payment.api.serializers import PaymentShowSerializer

FIELD_CODES = (
    # optional fields
    ('value', 201),
    ('currency', 201),
    ('date', 201),
    ('need_text', 201),
    ('is_active', 201),
    ('responsible', 201),

    # required fields
    ('user', 400),
    ('group', 400),
)


@pytest.mark.django_db
class TestPartnershipViewSet:
    @pytest.mark.parametrize(
        "field,code", FIELD_CODES, ids=[f[0] for f in FIELD_CODES])
    def test_create_user_without_one_field(
            self, monkeypatch, api_login_client, user_factory, currency_factory, partner_group_factory, field, code):
        monkeypatch.setattr(PartnershipViewSet, 'get_permissions', lambda self: [permissions.AllowAny()])
        url = reverse('partner-list')

        data = {
            'user': user_factory().id,
            'value': 20000,
            'currency': currency_factory().id,
            'date': date(2020, 2, 4),
            'need_text': 'Python is cool',
            'is_active': False,
            'responsible': user_factory().id,
            'group': partner_group_factory().id,
        }
        data.pop(field)
        response = api_login_client.post(url, data=data, format='json')

        assert response.status_code == code

    def test_update_need_with_need_text(self, api_login_supervisor_client, partner):
        url = reverse('partner-update-need', kwargs={'pk': partner.id})

        response = api_login_supervisor_client.put(url, data={'need_text': 'new text'})

        assert response.status_code == status.HTTP_200_OK
        assert Partnership.objects.get(id=partner.id).need_text == 'new text'

    def test_update_need_without_need_text(self, api_login_supervisor_client, partner):
        url = reverse('partner-update-need', kwargs={'pk': partner.id})

        response = api_login_supervisor_client.put(url, data={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_field(self, api_login_supervisor_client, partner, field_value):
        field, values = field_value
        url = reverse('partner-detail', kwargs={'pk': partner.id})

        setattr(partner, field, values[0])
        partner.save()

        response = api_login_supervisor_client.patch(url, data={field: values[1]})

        assert response.status_code == status.HTTP_200_OK
        assert getattr(Partnership.objects.get(pk=partner.id), field) == values[-1]

    @pytest.mark.hh
    def test_move_old_unclosed_deal_after_update_responsible(
            self, api_login_supervisor_client, user_factory, partner_factory, deal_factory):
        responsible = user_factory()
        partner = partner_factory(responsible=responsible)  # autocreate deal
        deal_factory.create_batch(2, date_created=timezone.now() + timedelta(days=-32), partnership=partner)

        assert partner.responsible == responsible
        assert responsible.disciples_deals.count() == 3

        url = reverse('partner-detail', kwargs={'pk': partner.id})
        api_login_supervisor_client.patch(url, data={'responsible': user_factory().id})

        partner.refresh_from_db()

        assert partner.responsible != responsible
        assert responsible.disciples_deals.count() == 0

    def test_list_of_partners_less_30(self, partner_factory, api_login_supervisor_client):
        partner_factory.create_batch(11)
        url = reverse('partner-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == Partnership.objects.count()

    def test_list_of_partners_eq_30(self, partner_factory, api_login_supervisor_client):
        partner_factory.create_batch(30 - Partnership.objects.count())
        url = reverse('partner-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == 30

    def test_list_of_partners_more_30(self, partner_factory, api_login_supervisor_client):
        partner_factory.create_batch(40)
        url = reverse('partner-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == 30

    def test_user_list_filter_by_hierarchy(
            self, monkeypatch, api_login_client, user_factory, partner_factory, hierarchy_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        other_hierarchy = hierarchy_factory()
        hierarchy = hierarchy_factory()
        partner_factory.create_batch(10, user__hierarchy=hierarchy)
        partner_factory.create_batch(20, user__hierarchy=other_hierarchy)

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?hierarchy={}'.format(url, hierarchy.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_department(
            self, monkeypatch, api_login_client, partner_factory, user_factory, department_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        other_department = department_factory()
        department = department_factory()
        partners = partner_factory.create_batch(10)
        for partner in partners:
            partner.user.departments.set([department])
        partners = partner_factory.create_batch(20)
        for partner in partners:
            partner.user.departments.set([other_department])

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?department={}'.format(url, department.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_master(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        master = partner_factory(user__username='master')
        # partner_factory.create_batch(10, user__master=master.user)
        for i in range(10):
            u = master.user.add_child(username='master{}'.format(i), master=master.user)
            partner_factory(user=u)
        partner_factory.create_batch(20)

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?master={}'.format(url, master.user.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_multi_master(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        master = partner_factory(user__username='master')
        other_master = partner_factory(user__username='other_master')
        # partner_factory.create_batch(10, user__master=master.user)
        for i in range(10):
            u = master.user.add_child(username='partner{}'.format(i), master=master.user)
            partner_factory(user=u)
        # partner_factory.create_batch(40, user__master=other_master.user)
        for i in range(40):
            u = other_master.user.add_child(username='other_partner{}'.format(i), master=other_master.user)
            partner_factory(user=u)
        partner_factory.create_batch(20)

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?master={}&master={}'.format(url, master.user.id, other_master.user.id),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 50

    def test_user_list_filter_by_master_tree(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        partner = partner_factory()  # count: + 0, = 0, all_users_count: +1, = 1

        # partner_factory.create_batch(3, user__master=partner.user)  # count: + 3, = 3, all_users_count: +3, = 4
        for i in range(3):
            u = partner.user.add_child(username='partner{}'.format(i), master=partner.user)
            partner_factory(user=u)
        # second_level_partner = partner_factory(user__master=partner.user)  # count: + 1, = 4, all_users_count: +1, = 5
        u = partner.user.add_child(username='second_partner', master=partner.user)
        second_level_partner = partner_factory(user=u)
        # partner_factory.create_batch(
        #     8, user__master=second_level_partner.user)  # count: + 8, = 12, all_users_count: +8, = 13
        for i in range(8):
            u = second_level_partner.user.add_child(
                username='second_partner{}'.format(i), master=second_level_partner.user)
            partner_factory(user=u)

        partner_factory.create_batch(15)  # count: + 0, = 12, all_users_count: +15, = 28
        other_partner = partner_factory()  # count: + 0, = 12, all_users_count: +1, = 29
        # partner_factory.create_batch(
        #     32, user__master=other_partner.user)  # count: + 0, = 12, all_users_count: + 32, = 61
        for i in range(32):
            u = other_partner.user.add_child(username='other_partner{}'.format(i), master=other_partner.user)
            partner_factory(user=u)

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(url, data={'master_tree': partner.user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 13

    def test_user_search_by_fio(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        partner_factory.create_batch(10)
        partner_factory(user__last_name='searchlast', user__first_name='searchfirst')

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_fio={}'.format(url, 'searchfirst searchlast'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_user_search_by_email(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        partner_factory.create_batch(10)
        partner_factory(user__email='mysupermail@test.com')
        partner_factory(user__email='test@mysupermail.com')

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_email={}'.format(url, 'mysupermail'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_phone(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        partner_factory.create_batch(10)
        partner_factory(user__phone_number='+380990002246')
        partner_factory(user__phone_number='+380992299000')

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_phone_number={}'.format(url, '99000'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_country(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        partner_factory.create_batch(10)
        partner_factory.create_batch(8, user__country='Ukraine')

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_country={}'.format(url, 'Ukraine'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_user_search_by_city(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_list_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.order_by('id'))
        partner_factory.create_batch(10)
        partner_factory.create_batch(8, user__city='Tokio')

        url = reverse('partner-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_city={}'.format(url, 'Tokio'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8


@pytest.mark.django_db
class TestDealViewSet:
    @pytest.mark.parametrize('is_responsible', (True, False))
    def test_create_payment(self, api_client, creator, is_responsible, deal, currency_factory):
        url = reverse('deal-create-payment', kwargs={'pk': deal.id})
        code = creator['code'][0] if is_responsible else creator['code'][1]

        if is_responsible:
            deal.partnership.responsible = creator['user']
            deal.partnership.save()

        api_client.force_login(creator['user'])
        api_login_client = api_client

        data = {
            'sum': '10',
            'description': 'no desc',
            'rate': '1.22',
            'sent_date': '2002-02-22',
            'currency': currency_factory().id,
        }
        response = api_login_client.post(url, data=data, format='json')

        assert response.status_code == code

        if code == status.HTTP_201_CREATED:
            payment = deal.payments.get()
            assert payment.sum == Decimal(data['sum'])
            assert payment.rate == Decimal(data['rate'])
            assert payment.description == data['description']
            assert payment.currency_sum_id == data['currency']
            assert payment.sent_date == datetime.strptime(data['sent_date'], '%Y-%m-%d').date()
            assert response.data == PaymentShowSerializer(payment).data

    @pytest.mark.parametrize('is_responsible', (True, False))
    def test_payments(self, api_client, viewer, is_responsible, deal, payment_factory):
        payment_factory.create_batch(6, purpose=deal)
        url = reverse('deal-payments', kwargs={'pk': deal.id})
        code = viewer['code'][0] if is_responsible else viewer['code'][1]

        if is_responsible:
            deal.partnership.responsible = viewer['user']
            deal.partnership.save()

        api_client.force_login(viewer['user'])

        response = api_client.get(url, format='json')

        assert response.status_code == code
        if code == status.HTTP_200_OK:
            assert response.data == PaymentShowSerializer(deal.payments.all(), many=True).data

    def test_list_of_deals_less_30(self, deal_factory, api_login_supervisor_client):
        deal_factory.create_batch(11)
        url = reverse('deal-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == Deal.objects.count()

    def test_list_of_deals_eq_30(self, deal_factory, api_login_supervisor_client):
        deal_factory.create_batch(30 - Deal.objects.count())
        url = reverse('deal-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == 30

    def test_list_of_deals_more_30(self, deal_factory, api_login_supervisor_client):
        deal_factory.create_batch(40)
        url = reverse('deal-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == 30

    @pytest.mark.parametrize('method,action,serializer_class', (
            ('get', 'list', DealSerializer),
            ('post', 'create', DealCreateSerializer),
            ('get', 'retrieve', DealSerializer),
            ('put', 'update', DealUpdateSerializer),
            ('patch', 'partial_update', DealUpdateSerializer),
    ), ids=('get-list', 'post-create', 'get-retrieve', 'put-update', 'patch-partial_update'))
    def test_get_serializer_class(self, rf, partner, fake_deal_view_set, method, action, serializer_class):
        method_action = getattr(rf, method)
        request = method_action('/')
        request.user = partner.user
        view = fake_deal_view_set.as_view({method: action})

        instance = view(request, pk=1)

        assert instance.get_serializer_class() == serializer_class
