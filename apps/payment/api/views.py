# -*- coding: utf-8
from __future__ import unicode_literals

from django.db.models import Value as V
from django.db.models.functions import Concat
from django_filters import rest_framework
from rest_framework import mixins, filters
from rest_framework.generics import GenericAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.account.api.serializers import UserForSelectSerializer
from apps.account.models import CustomUser
from apps.analytics.decorators import log_perform_update, log_perform_destroy
from apps.analytics.mixins import LogAndCreateUpdateDestroyMixin
from apps.payment.api.filters import (
    PaymentFilterByPurpose, PaymentFilter, FilterByDealFIO, FilterByDealDate,
    FilterByDealManager, FilterByChurchReportDate, FilterByChurchReportPastor,
    FilterByChurchReportChurchTitle, FilterByDealType, FilterByPaymentCurrency, FilterByDeal)
from apps.payment.api.pagination import PaymentPagination, ChurchReportPaymentPagination
from apps.payment.api.permissions import PaymentManagerOrSupervisor
from apps.payment.api.serializers import (
    PaymentUpdateSerializer, PaymentShowSerializer, PaymentDealShowSerializer, PaymentChurchReportShowSerializer)
from apps.payment.models import Payment
from apps.payment.resources import PaymentResource
from common.filters import FieldSearchFilter
from common.pagination import ForSelectPagination
from common.test_helpers.utils import get_real_user
from common.views_mixins import ExportViewSetMixin

COMMON_PAYMENTS_ORDERING_FIELDS = ('sum', 'effective_sum', 'currency_sum__name', 'currency_rate__name', 'created_at',
                                   'sent_date', 'manager__last_name', 'description',)


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


class PaymentDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentShowSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return self.queryset.for_user_by_all(user)

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Payment, pk=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PaymentDealListView(mixins.ListModelMixin, GenericAPIView, ExportViewSetMixin):
    queryset = Payment.objects.base_queryset()
    serializer_class = PaymentDealShowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PaymentPagination

    filter_backends = (rest_framework.DjangoFilterBackend,
                       FieldSearchFilter,

                       # FilterByDealFIO,
                       # FilterByDealDate,
                       # # FilterByDealManagerFIO,
                       # FilterByDealManager,
                       # FilterByDealType,
                       FilterByDeal,

                       filters.OrderingFilter,
                       FilterByPaymentCurrency,)
    ordering_fields = COMMON_PAYMENTS_ORDERING_FIELDS + (
        # 'deals__partnership__user__last_name',
        # 'deals__date_created',
        # 'deals__partnership__responsible__last_name',
        # 'deals__responsible__last_name',
        # 'deals__type'
    )

    field_search_fields = {
        'search_description': ('description',),
    }
    filter_class = PaymentFilter

    resource_class = PaymentResource

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return self.queryset.add_deal_fio()

    def post(self, request, *args, **kwargs):
        """For export/import to excel"""
        return self._export(request, *args, **kwargs)


class PaymentChurchReportListView(mixins.ListModelMixin, GenericAPIView):
    queryset = Payment.objects.base_queryset()
    serializer_class = PaymentChurchReportShowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = ChurchReportPaymentPagination

    filter_backends = (rest_framework.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,
                       FilterByChurchReportDate,
                       FilterByChurchReportPastor,
                       FilterByChurchReportChurchTitle,
                       FilterByPaymentCurrency,)

    ordering_fields = COMMON_PAYMENTS_ORDERING_FIELDS + ('church_reports__church__pastor__last_name',
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


class PaymentSupervisorListView(mixins.ListModelMixin, GenericAPIView):
    serializer_class = UserForSelectSerializer
    pagination_class = ForSelectPagination

    filter_backends = (filters.SearchFilter,)
    search_fields = ('first_name', 'last_name', 'middle_name')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return CustomUser.objects.filter(checks__isnull=False).annotate(
            full_name=Concat('last_name', V(' '),
                             'first_name', V(' '),
                             'middle_name')
        ).order_by('last_name').distinct("id", "last_name")

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('without_pagination', None) is not None:
            return None
        return super().paginate_queryset(queryset)
