from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from partnership.models import Partnership, Deal
from partnership.serializers import PartnershipForEditSerializer
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
