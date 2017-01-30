from datetime import date, datetime
from decimal import Decimal
from json import dumps

from channels import Group
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.settings import api_settings

from partnership.models import Partnership, Deal
from payment.permissions import PaymentPermission
from payment.serializers import PaymentCreateSerializer, PaymentShowSerializer
from summit.models import SummitAnket


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


class PaymentCheckPermissionMixin:
    payment_permission_classes = (PaymentPermission,)
    payment_permission_message = None
    payment_permission_invalid_object_message = _("This object don't have payments.")

    def get_payment_permissions(self):
        return [permission() for permission in self.payment_permission_classes]

    def check_payment_permissions(self, request, purpose):
        if isinstance(purpose, (Partnership, Deal)):
            method_name = 'has_object_permission'
            args = (request, self, purpose)
        elif isinstance(purpose, SummitAnket):
            method_name = 'has_object_permission'
            args = (request, self, purpose.summit)
        else:  # pragma: no cover
            raise exceptions.PermissionDenied(detail=self.payment_permission_invalid_object_message)

        for permission in self.get_payment_permissions():
            if not getattr(permission, method_name)(*args):
                raise exceptions.PermissionDenied(
                    detail=getattr(permission, 'message', self.payment_permission_message))


class CreatePaymentMixin(PaymentCheckPermissionMixin):
    create_payment_serializer = PaymentCreateSerializer
    show_payment_serializer = PaymentShowSerializer

    def get_queryset(self):  # pragma: no cover
        raise NotImplementedError()

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    @detail_route(methods=['post'])
    def create_payment(self, request, pk=None):
        purpose_model = self.get_queryset().model
        purpose = get_object_or_404(purpose_model, pk=pk)
        self.check_payment_permissions(request, purpose)

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

        data = {
            'user_id': request.user.id,
            'editor_name': request.user.fullname,
            'sum': payment.effective_sum_str,
        }
        Group("payments_{}".format(purpose.user.id)).send({'text': dumps(data)})

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListPaymentMixin(PaymentCheckPermissionMixin):
    list_payment_serializer = PaymentShowSerializer
    payment_list_field = 'payments'

    def get_queryset(self):  # pragma: no cover
        raise NotImplementedError()

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    @detail_route(methods=['get'])
    def payments(self, request, pk=None):
        purpose_model = self.get_queryset().model
        purpose = get_object_or_404(purpose_model, pk=pk)
        self.check_payment_permissions(request, purpose)

        queryset = getattr(purpose, self.payment_list_field).select_related('currency_sum', 'currency_rate', 'manager')

        serializer = self.list_payment_serializer(queryset, many=True)

        return Response(serializer.data)
