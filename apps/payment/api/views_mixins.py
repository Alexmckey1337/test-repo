from decimal import Decimal
from json import dumps

from channels import Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from apps.partnership.models import Deal, ChurchDeal
from apps.payment.models import Currency
from apps.payment.api.permissions import PaymentPermission
from apps.payment.api.serializers import PaymentCreateSerializer, PaymentShowSerializer
from apps.summit.models import SummitAnket
from apps.event.models import ChurchReport


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


class PaymentCheckPermissionMixin:
    payment_permission_classes = (IsAuthenticated, PaymentPermission,)
    payment_permission_message = None
    payment_permission_invalid_object_message = _("This object don't have payments.")

    def get_payment_permissions(self):
        return [permission() for permission in self.payment_permission_classes]

    def check_payment_permissions(self, request, purpose):
        if isinstance(purpose, (ChurchDeal, Deal)):
            args = (request, self, purpose)
        elif isinstance(purpose, SummitAnket):
            args = (request, self, purpose.summit)
        elif isinstance(purpose, ChurchReport):
            args = (request, self, purpose)
        else:  # pragma: no cover
            raise exceptions.PermissionDenied(detail=self.payment_permission_invalid_object_message)

        for permission in self.get_payment_permissions():
            if not permission.has_object_permission(*args):
                raise exceptions.PermissionDenied(
                    detail=getattr(permission, 'message', self.payment_permission_message))


class CreatePaymentMixin(PaymentCheckPermissionMixin):
    create_payment_serializer = PaymentCreateSerializer
    show_payment_serializer = PaymentShowSerializer

    def get_queryset(self):  # pragma: no cover
        raise NotImplementedError()

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    @staticmethod
    def get_currency(body, purpose, force_currency=None):
        if force_currency:
            return force_currency.id
        return body.get('currency', purpose.currency.id)

    def _create_payment(self, request, pk=None, currency=None):
        purpose_model = self.get_queryset().model
        purpose = get_object_or_404(purpose_model, pk=pk)
        self.check_payment_permissions(request, purpose)

        body = request.data
        sum = body.get('sum', None)
        description = body.get('description', '')
        rate = body.get('rate', Decimal(1))
        operation = body.get('operation', '*')
        currency = self.get_currency(body, purpose, currency)
        sent_date = body.get('sent_date')
        if not sent_date:
            sent_date = timezone.now().strftime('%Y-%m-%d')
        if rate == 1 and currency != purpose.currency.id:
            print(rate, currency, purpose.currency)
            raise ValidationError({'detail': _('Rate must be not 1.00')})
        data = {
            'sum': sum,
            'rate': rate,
            'operation': operation,
            'currency_sum': currency,
            'sent_date': sent_date,
            'description': description,
            'manager': request.user.id,
            'content_type': ContentType.objects.get_for_model(purpose_model).id,
            'object_id': pk,
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
        # if purpose_model not in
        if not isinstance(purpose, ChurchReport) and not isinstance(purpose, ChurchDeal):
            Group("payments_{}".format(purpose.user.id)).send({'text': dumps(data)})

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
        return self._create_payment(request, pk)

    @action(detail=True, methods=['post'])
    def create_uah_payment(self, request, pk=None):
        try:
            uah = Currency.objects.get(code='uah')
        except Currency.DoesNotExist:
            return Response({'detail': _('UAH does not exist')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return self._create_payment(request, pk, uah)


class ListPaymentMixin(PaymentCheckPermissionMixin):
    list_payment_serializer = PaymentShowSerializer
    payment_list_field = 'payments'

    def get_queryset(self):  # pragma: no cover
        raise NotImplementedError()

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    def _payments(self, request, pk=None):
        purpose_model = self.get_queryset().model
        purpose = get_object_or_404(purpose_model, pk=pk)
        self.check_payment_permissions(request, purpose)

        queryset = getattr(purpose, self.payment_list_field).select_related(
            'currency_sum', 'currency_rate', 'manager')

        serializer = self.list_payment_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        return self._payments(request, pk)
