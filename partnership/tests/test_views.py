# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from datetime import datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status, permissions

from account.models import CustomUser
from partnership.models import Partnership, Deal
from partnership.serializers import PartnershipForEditSerializer, DealSerializer, DealCreateSerializer
from partnership.views import PartnershipViewSet
from payment.serializers import PaymentShowSerializer


@pytest.mark.django_db
class TestPartnershipViewSet:
    @pytest.mark.parametrize('is_responsible', (True, False))
    def test_create_payment(self, api_client, creator, is_responsible, partner, currency_factory):
        url = reverse('partnerships_v1_1-create-payment', kwargs={'pk': partner.id})
        code = creator['code'][0] if is_responsible else creator['code'][1]

        if is_responsible:
            partner.responsible = creator['partner']
            partner.save()

        api_client.force_login(creator['partner'].user)
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
            payment = partner.extra_payments.get()
            assert payment.sum == Decimal(data['sum'])
            assert payment.rate == Decimal(data['rate'])
            assert payment.description == data['description']
            assert payment.currency_sum_id == data['currency']
            assert payment.sent_date == datetime.strptime(data['sent_date'], '%Y-%m-%d').date()
            assert response.data == PaymentShowSerializer(payment).data

    @pytest.mark.parametrize('is_responsible', (True, False))
    def test_payments(self, api_client, viewer, is_responsible, partner, payment_factory):
        payment_factory.create_batch(6, purpose=partner)
        url = reverse('partnerships_v1_1-payments', kwargs={'pk': partner.id})
        code = viewer['code'][0] if is_responsible else viewer['code'][1]

        if is_responsible:
            partner.responsible = viewer['partner']
            partner.save()

        api_client.force_login(viewer['partner'].user)
        api_login_client = api_client

        response = api_login_client.get(url, format='json')

        assert response.status_code == code
        if code == status.HTTP_200_OK:
            assert response.data == PaymentShowSerializer(partner.extra_payments.all(), many=True).data

    def test_simple(self, api_login_client, partner_factory):
        partner_factory(level=Partnership.MANAGER + 1)
        partner_factory.create_batch(2, level=Partnership.MANAGER)
        partner_factory.create_batch(4, level=Partnership.MANAGER - 1)

        url = reverse('partnerships_v1_1-simple')

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 6

    def test_for_edit_user_is_partner(self, api_login_client, partner):
        url = reverse('partnerships_v1_1-for-edit')

        response = api_login_client.get(url, data={'user': partner.user_id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == PartnershipForEditSerializer(partner).data

    def test_for_edit_user_is_not_partner(self, api_login_client, user_factory):
        url = reverse('partnerships_v1_1-for-edit')

        response = api_login_client.get(url, data={'user': user_factory().id})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_need_with_need_text(self, api_login_supervisor_client, partner):
        url = reverse('partnerships_v1_1-update-need', kwargs={'pk': partner.id})

        response = api_login_supervisor_client.put(url, data={'need_text': 'new text'})

        assert response.status_code == status.HTTP_200_OK
        assert Partnership.objects.get(id=partner.id).need_text == 'new text'

    def test_update_need_without_need_text(self, api_login_client, partner):
        url = reverse('partnerships_v1_1-update-need', kwargs={'pk': partner.id})

        response = api_login_client.put(url, data={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_field(self, api_login_supervisor_client, partner, field_value):
        field, values = field_value
        url = reverse('partnerships_v1_1-detail', kwargs={'pk': partner.id})

        setattr(partner, field, values[0])
        partner.save()

        response = api_login_supervisor_client.patch(url, data={field: values[1]})

        assert response.status_code == status.HTTP_200_OK
        assert getattr(Partnership.objects.get(pk=partner.id), field) == values[-1]

    def test_list_of_partners_less_30(self, partner_factory, api_login_supervisor_client):
        partner_factory.create_batch(11)
        url = reverse('partnerships_v1_1-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == Partnership.objects.count()

    def test_list_of_partners_eq_30(self, partner_factory, api_login_supervisor_client):
        partner_factory.create_batch(30 - Partnership.objects.count())
        url = reverse('partnerships_v1_1-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == 30

    def test_list_of_partners_more_30(self, partner_factory, api_login_supervisor_client):
        partner_factory.create_batch(40)
        url = reverse('partnerships_v1_1-list')

        response = api_login_supervisor_client.get(url)

        assert len(response.data['results']) == 30

    def test_user_list_filter_by_hierarchy(self, monkeypatch, api_login_client, user_factory, partner_factory, hierarchy_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        other_hierarchy = hierarchy_factory()
        hierarchy = hierarchy_factory()
        partner_factory.create_batch(10, user__hierarchy=hierarchy)
        partner_factory.create_batch(20, user__hierarchy=other_hierarchy)

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?hierarchy={}'.format(url, hierarchy.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_department(self, monkeypatch, api_login_client, partner_factory, user_factory, department_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        other_department = department_factory()
        department = department_factory()
        partners = partner_factory.create_batch(10)
        for partner in partners:
            partner.user.departments.set([department])
        partners = partner_factory.create_batch(20)
        for partner in partners:
            partner.user.departments.set([other_department])

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?department={}'.format(url, department.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_master(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        master = partner_factory(user__username='master')
        partner_factory.create_batch(10, user__master=master.user)
        partner_factory.create_batch(20)

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get('{}?master={}'.format(url, master.user.id), format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_user_list_filter_by_multi_master(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        master = partner_factory(user__username='master')
        other_master = partner_factory(user__username='other_master')
        partner_factory.create_batch(10, user__master=master.user)
        partner_factory.create_batch(40, user__master=other_master.user)
        partner_factory.create_batch(20)

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?master={}&master={}'.format(url, master.user.id, other_master.user.id),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 50

    def test_user_list_filter_by_master_tree(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        partner = partner_factory()  # count: + 0, = 0, all_users_count: +1, = 1

        partner_factory.create_batch(3, user__master=partner.user)  # count: + 3, = 3, all_users_count: +3, = 4
        second_level_partner = partner_factory(user__master=partner.user)  # count: + 1, = 4, all_users_count: +1, = 5
        partner_factory.create_batch(
            8, user__master=second_level_partner.user)  # count: + 8, = 12, all_users_count: +8, = 13

        partner_factory.create_batch(15)  # count: + 0, = 12, all_users_count: +15, = 28
        other_partner = partner_factory()  # count: + 0, = 12, all_users_count: +1, = 29
        partner_factory.create_batch(
            32, user__master=other_partner.user)  # count: + 0, = 12, all_users_count: + 32, = 61

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(url, data={'master_tree': partner.user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 13

    def test_user_search_by_fio(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        partner_factory.create_batch(10)
        partner_factory(user__last_name='searchlast', user__first_name='searchfirst')

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_fio={}'.format(url, 'searchfirst searchlast'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_user_search_by_email(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        partner_factory.create_batch(10)
        partner_factory(user__email='mysupermail@test.com')
        partner_factory(user__email='test@mysupermail.com')

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_email={}'.format(url, 'mysupermail'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_phone(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        partner_factory.create_batch(10)
        partner_factory(user__phone_number='+380990002246')
        partner_factory(user__phone_number='+380992299000')

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_phone_number={}'.format(url, '99000'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_user_search_by_country(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        partner_factory.create_batch(10)
        partner_factory.create_batch(8, user__country='Ukraine')

        url = reverse('partnerships_v1_1-list')

        api_login_client.force_login(user=user_factory(is_staff=True))
        response = api_login_client.get(
            '{}?search_country={}'.format(url, 'Ukraine'),
            format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 8

    def test_user_search_by_city(self, monkeypatch, api_login_client, partner_factory, user_factory):
        monkeypatch.setattr(PartnershipViewSet, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(PartnershipViewSet, 'get_queryset', lambda self: Partnership.objects.all())
        partner_factory.create_batch(10)
        partner_factory.create_batch(8, user__city='Tokio')

        url = reverse('partnerships_v1_1-list')

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
            deal.partnership.responsible = creator['partner']
            deal.partnership.save()

        api_client.force_login(creator['partner'].user)
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
            deal.partnership.responsible = viewer['partner']
            deal.partnership.save()

        api_client.force_login(viewer['partner'].user)

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
            ('put', 'update', DealSerializer),
            ('patch', 'partial_update', DealSerializer),
    ), ids=('get-list', 'post-create', 'get-retrieve', 'put-update', 'patch-partial_update'))
    def test_get_serializer_class(self, rf, fake_deal_view_set, method, action, serializer_class):
        method_action = getattr(rf, method)
        request = method_action('/')
        view = fake_deal_view_set.as_view({method: action})

        instance = view(request, pk=1)

        assert instance.get_serializer_class() == serializer_class
