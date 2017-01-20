from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

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
