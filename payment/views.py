# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import mixins, filters
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from analytics.decorators import log_perform_update, log_perform_destroy
from analytics.mixins import LogAndCreateUpdateDestroyMixin
from common.filters import FieldSearchFilter
from common.test_helpers.utils import get_real_user
from payment.filters import (PaymentFilterByPurpose, PaymentFilter, FilterByDealFIO, FilterByDealDate,
                             FilterByDealManager, FilterByChurchReportDate,
                             FilterByChurchReportPastor, FilterByChurchReportChurchTitle)
from payment.serializers import (PaymentUpdateSerializer, PaymentShowSerializer, PaymentDealShowSerializer,
                                 PaymentChurchReportShowSerializer)
from .models import Payment
from .permissions import PaymentManagerOrSupervisor
from .pagination import PaymentPagination, ChurchReportPaymentPagination


class PaymentUpdateDestroyView(LogAndCreateUpdateDestroyMixin,
                               mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentUpdateSerializer
    permission_classes = (IsAuthenticated, PaymentManagerOrSupervisor)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.old_data = serializer.instance.get_data_for_deal_purpose_update()
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @log_perform_update
    def perform_update(self, serializer, **kwargs):
        new_obj = kwargs.get('new_obj')
        self._update_purpose(self.old_data, new_obj.get_data_for_deal_purpose_update(), new_obj)

    @log_perform_destroy
    def perform_destroy(self, instance, **kwargs):
        instance.delete()
        instance.purpose.update_after_cancel_payment(
            editor=get_real_user(self.request), payment=instance)

    # Helpers

    def _update_purpose(self, old_data, new_data, payment):
        purpose = old_data.pop('purpose')

        if payment.content_type.model == 'deal':
            if any(map(lambda k: old_data[k] != new_data[k], old_data.keys())):
                purpose.update_after_cancel_payment(
                    editor=get_real_user(self.request), payment=payment)
        else:
            purpose.update_after_cancel_payment(
                editor=get_real_user(self.request), payment=payment)


class PaymentListView(mixins.ListModelMixin, GenericAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentShowSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (PaymentFilterByPurpose,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        return self.queryset.for_user_by_all(user)


class PaymentDetailView(mixins.RetrieveModelMixin, GenericAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentShowSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        return self.queryset.for_user_by_all(user)


class PaymentDealListView(mixins.ListModelMixin, GenericAPIView):
    queryset = Payment.objects.base_queryset()
    serializer_class = PaymentDealShowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PaymentPagination

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       FilterByDealFIO,
                       FilterByDealDate,
                       # FilterByDealManagerFIO,
                       FilterByDealManager,
                       filters.OrderingFilter,)
    ordering_fields = ('sum', 'effective_sum', 'currency_sum__name', 'currency_rate__name',
                       'created_at', 'sent_date', 'manager__last_name', 'description',
                       'deals__partnership__user__last_name', 'deals__date_created',
                       'deals__partnership__responsible__user__last_name')

    field_search_fields = {
        'search_description': ('description',),
    }
    filter_class = PaymentFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        return self.queryset.for_user_by_deal(user).add_deal_fio()


class PaymentChurchReportListView(mixins.ListModelMixin, GenericAPIView):
    queryset = Payment.objects.base_queryset()
    serializer_class = PaymentChurchReportShowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = ChurchReportPaymentPagination

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       FilterByChurchReportPastor,
                       filters.OrderingFilter,
                       FilterByChurchReportDate,
                       FilterByChurchReportPastor,
                       FilterByChurchReportChurchTitle,)

    ordering_fields = ('sum', 'effective_sum', 'currency_sum__name', 'currency_rate__name', 'created_at',
                       'sent_date', 'manager__last_name', 'description',
                       'church_reports__church__pastor__last_name',
                       'church_reports__date', 'church_reports__church__title')

    field_search_fields = {
        'search_title': ('church_reports__church__pastor__last_name',
                         'church_reports__church__pastor__first_name',
                         'church_reports__church__pastor__middle_name',
                         'church_reports__church__title')
    }

    filter_class = PaymentFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        return self.queryset.for_user_by_church_report(user).add_church_report_info()
