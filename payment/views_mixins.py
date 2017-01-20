from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.settings import api_settings

from payment.serializers import PaymentCreateSerializer, PaymentShowSerializer


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


class CreatePaymentMixin:
    create_payment_serializer = PaymentCreateSerializer
    show_payment_serializer = PaymentShowSerializer

    def get_queryset(self):
        raise NotImplementedError()

    def get_object(self):
        raise NotImplementedError()

    @detail_route(methods=['post'])
    def create_payment(self, request, pk=None):
        purpose_model = self.get_queryset().model
        purpose = self.get_object()

        sum = request.data['sum']
        description = request.data.get('description', '')
        rate = request.data.get('rate', Decimal(1))
        currency = request.data.get('currency', purpose.currency.id)

        data = {
            'sum': sum,
            'rate': rate,
            'currency_sum': currency,
            'description': description,
            'manager': request.user.id,
            'content_type': ContentType.objects.get_for_model(purpose_model).id,
            'object_id': pk
        }
        serializer = self.create_payment_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        payment = serializer.save()
        serializer = self.show_payment_serializer(payment)

        headers = get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListPaymentMixin:
    list_payment_serializer = PaymentShowSerializer
    payment_list_field = 'payments'

    def get_queryset(self):
        raise NotImplementedError()

    def get_object(self):
        raise NotImplementedError()

    @detail_route(methods=['get'])
    def payments(self, request, pk=None):
        purpose = self.get_object()
        queryset = getattr(purpose, self.payment_list_field).select_related('currency_sum', 'currency_rate', 'manager')

        serializer = self.list_payment_serializer(queryset, many=True)

        return Response(serializer.data)
