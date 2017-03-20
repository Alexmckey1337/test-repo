# -*- coding: utf-8
from __future__ import unicode_literals

from django.db.models import Q
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from partnership.models import Partnership, Deal
from payment.filters import PaymentFilterByPurpose
from payment.serializers import PaymentUpdateSerializer, PaymentShowSerializer
from summit.models import SummitAnket
from .models import Payment
from .permissions import PaymentManagerOrSupervisor


class PaymentUpdateDestroyView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentUpdateSerializer
    permission_classes = (PaymentManagerOrSupervisor,)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        old_data = serializer.instance.get_data_for_deal_purpose_update()

        payment = serializer.save()

        self._update_purpose(old_data, payment.get_data_for_deal_purpose_update(), payment.content_type)

    def perform_destroy(self, instance):
        instance.delete()
        instance.purpose.update_after_cancel_payment()

    # Helpers

    @staticmethod
    def _update_purpose(old_data, new_data, content_type):
        purpose = old_data.pop('purpose')

        if content_type.model == 'deal':
            if any(map(lambda k: old_data[k] != new_data[k], old_data.keys())):
                purpose.update_after_cancel_payment()
        else:
            purpose.update_after_cancel_payment()


class PaymentListView(mixins.ListModelMixin, GenericAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentShowSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (PaymentFilterByPurpose,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        deal_ids = Deal.objects.for_user(user).values_list('id', flat=True)
        partner_ids = Partnership.objects.for_user(user).values_list('id', flat=True)
        anket_ids = SummitAnket.objects.for_user(user).values_list('id', flat=True)

        return self.queryset.filter(
            (Q(content_type__model='deal') & Q(object_id__in=deal_ids)) |
            (Q(content_type__model='partnership') & Q(object_id__in=partner_ids)) |
            (Q(content_type__model='summitanket') & Q(object_id__in=anket_ids))
        )
