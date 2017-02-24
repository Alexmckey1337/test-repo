# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import mixins
from rest_framework.generics import GenericAPIView

from payment.serializers import PaymentUpdateSerializer
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
