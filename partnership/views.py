# -*- coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict
from decimal import Decimal

import django_filters
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Case, IntegerField, Sum, Value, When
from django.db.models import F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import api_view, list_route, detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser as User, CustomUser
from common.views_mixins import ExportViewSetMixin
from navigation.table_fields import user_table, partner_table
from partnership.permissions import (
    CanCreatePartnerPayment, CanClosePartnerDeal, IsManagerOrHigh)
from partnership.resources import PartnerResource
from payment.models import Currency
from payment.views_mixins import CreatePaymentMixin, ListPaymentMixin
from .models import Partnership, Deal
from .serializers import (
    DealSerializer, PartnershipSerializer, DealCreateSerializer,
    PartnershipUnregisterUserSerializer, PartnershipForEditSerializer, PartnershipTableSerializer)


class PartnershipPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'common_table': partner_table(self.request.user),
            'user_table': user_table(self.request.user, prefix_ordering_title='user__'),
            'results': data
        })


class DealPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('check_payment_permissions', CanCreatePartnerPayment().has_permission(self.request, None)),
            ('can_close_deal', CanClosePartnerDeal().has_permission(self.request, None)),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class PartnerStatMixin:
    @list_route(methods=['get'])
    def stats_payments(self, request):
        current_partner = get_object_or_404(Partnership, user=request.user)

        self.check_stats_permissions(current_partner)

        deals = self.get_deals_of_partner(request, current_partner)
        deals = self.filter_deals_by_month(request, deals)
        # deals = Deal.objects.all()  # for test, del this
        stats = dict()

        deals_with_sum = deals.annotate_total_sum()

        stats['deals'] = self.stats_by_deals(deals, deals_with_sum)
        stats['partners'] = self.stats_by_partners(deals, deals_with_sum)
        stats['sum'] = self.stats_by_sum(deals, deals_with_sum)

        return Response(stats)

    # Helpers

    @staticmethod
    def check_stats_permissions(current_partner):
        if current_partner.level > Partnership.MANAGER:
            raise PermissionDenied({'detail': _('Статистику можно просматривать только менеджерам.')})

    @staticmethod
    def get_deals_of_partner(request, current_partner):
        request_partner_id = request.query_params.get('partner_id')

        if current_partner.level == Partnership.MANAGER or not request_partner_id:
            return current_partner.disciples_deals
        if request_partner_id == 'all':
            return Deal.objects.filter(responsible__isnull=False)
        partner = get_object_or_404(Partnership, id=request_partner_id)
        return partner.disciples_deals

    @staticmethod
    def filter_deals_by_month(request, deals):
        month = request.query_params.get('month', timezone.now().month)
        year = request.query_params.get('year', timezone.now().year)

        return deals.filter(date_created__month=month, date_created__year=year)

    @staticmethod
    def stats_by_deals(deals, deals_with_sum):
        paid = deals_with_sum.filter(total_sum__gte=F('value')).count()
        unpaid = deals_with_sum.filter(total_sum__lt=F('value'), total_sum=Decimal(0)).count()
        partial_paid = deals_with_sum.filter(total_sum__lt=F('value'), total_sum__gt=Decimal(0)).count()
        deals_result = {
            'paid_count': paid,
            'unpaid_count': unpaid,
            'partial_paid_count': partial_paid
        }

        closed_count = deals.aggregate(
            closed_count=Sum(
                Case(When(done=True, then=1), default=0,
                     output_field=IntegerField())
            ),
            unclosed_count=Sum(
                Case(When(done=False, then=1), default=0,
                     output_field=IntegerField())
            ))
        deals_result.update(closed_count)

        return deals_result

    @staticmethod
    def stats_by_partners(deals, deals_with_sum):
        paid = set(deals_with_sum.filter(total_sum__gte=F('value')).aggregate(p=ArrayAgg('partnership'))['p'])
        unpaid = set(deals_with_sum.filter(
            total_sum__lt=F('value'),
            total_sum=Decimal(0)).aggregate(p=ArrayAgg('partnership'))['p'])
        partial_paid = set(deals_with_sum.filter(
            total_sum__lt=F('value'),
            total_sum__gt=Decimal(0)).aggregate(p=ArrayAgg('partnership'))['p'])
        paid_count = len(paid - unpaid - partial_paid)
        unpaid_count = len(unpaid - partial_paid - paid)
        partial_paid_count = len(partial_paid | (paid & unpaid))

        closed = set(deals.filter(done=True).aggregate(p=ArrayAgg('partnership'))['p'])
        unclosed = set(deals.filter(done=False).aggregate(p=ArrayAgg('partnership'))['p'])
        closed_count = len(closed - unclosed)
        unclosed_count = len(unclosed)

        return {
            'paid_count': paid_count,
            'unpaid_count': unpaid_count,
            'partial_paid_count': partial_paid_count,
            'closed_count': closed_count,
            'unclosed_count': unclosed_count
        }

    @staticmethod
    def stats_by_sum(deals, deals_with_sum):
        sum = dict()
        currencies = set(
            deals.aggregate(currency_codes=ArrayAgg('currency__code'))['currency_codes'])

        for c in Currency.objects.filter(code__in=currencies):
            total_paid_sum = deals_with_sum.filter(currency=c).aggregate(
                sum_planed=Coalesce(Sum('value'), Value(0)),
                sum_paid=Coalesce(Sum('total_sum'), Value(0)))
            closed_paid_sum = deals_with_sum.filter(currency=c, done=True).aggregate(
                sum_planed=Coalesce(Sum('value'), Value(0)),
                sum_paid=Coalesce(Sum('total_sum'), Value(0)))
            sum[c.code] = {
                'currency_name': c.name,
                'total_paid_sum': total_paid_sum,
                'closed_paid_sum': closed_paid_sum
            }
        return sum


class PartnershipViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet,
                         CreatePaymentMixin,
                         ListPaymentMixin,
                         ExportViewSetMixin,
                         PartnerStatMixin):
    queryset = Partnership.objects.base_queryset().order_by(
        'user__last_name', 'user__first_name', 'user__middle_name')
    serializer_class = PartnershipSerializer
    serializer_read_class = PartnershipTableSerializer
    pagination_class = PartnershipPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('user', 'responsible__user', 'responsible')
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name', 'user__search_name',
                     'user__country', 'user__region', 'user__city', 'user__district',
                     'user__address', 'user__skype', 'user__phone_number', 'user__hierarchy__title',
                     'user__email',)
    ordering_fields = ('user__first_name', 'user__last_name', 'user__master__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__facebook',
                       'user__vkontakte', 'value', 'responsible__user__last_name')
    permission_classes = (IsAuthenticated,)

    payment_list_field = 'extra_payments'
    resource_class = PartnerResource

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return self.serializer_read_class
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.for_user(user=self.request.user)

    @list_route()
    def simple(self, request):
        partnerships = Partnership.objects.select_related('user').filter(
            level__lte=Partnership.MANAGER).values_list(
            'id', 'user__last_name', 'user__first_name', 'user__middle_name')
        partnerships = [{'id': p[0], 'fullname': '{} {} {}'.format(*p[1:])} for p in partnerships]
        return Response(partnerships)

    # TODO deprecated
    @list_route()
    def for_edit(self, request):
        user_id = request.query_params.get('user')
        user = get_object_or_404(CustomUser, pk=user_id)
        partnership = get_object_or_404(Partnership, user=user)

        data = PartnershipForEditSerializer(partnership).data
        return Response(data)

    # TODO deprecated
    @detail_route(methods=['put'])
    def update_need(self, request, pk=None):
        text = request.data.get('need_text', None)
        if text is None:
            return Response({'detail': _("'need_text' is required field.")}, status=status.HTTP_400_BAD_REQUEST)
        partnership = self.get_object()
        partnership.need_text = text
        partnership.save()

        return Response({'need_text': text})


class DateFilter(filters.FilterSet):
    to_date = django_filters.DateFilter(name="date_created", lookup_type='lte')
    from_date = django_filters.DateFilter(name="date_created", lookup_type='gte')

    class Meta:
        model = Deal
        fields = ['partnership__responsible__user',
                  'partnership__user', 'value', 'date_created', 'date',
                  'expired', 'done', 'to_date', 'from_date', ]


class DealViewSet(mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet,
                  CreatePaymentMixin,
                  ListPaymentMixin):
    queryset = Deal.objects.base_queryset(). \
        annotate_full_name(). \
        annotate_responsible_name(). \
        annotate_total_sum(). \
        order_by('-date_created', 'id')
    serializer_class = DealSerializer
    serializer_create_class = DealCreateSerializer
    pagination_class = DealPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_class = DateFilter
    search_fields = ('partnership__user__first_name',
                     'partnership__user__last_name',
                     'partnership__user__search_name',
                     'partnership__user__middle_name',)
    permission_classes = (IsManagerOrHigh,)

    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_create_class
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        if Partnership.objects.get(user=user).level < Partnership.MANAGER:
            return self.queryset
        return self.queryset.filter(partnership__responsible__user=user)


class PartnershipsUnregisterUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(partnership__isnull=True)
    serializer_class = PartnershipUnregisterUserSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.DjangoFilterBackend,)
    filter_fields = ('partnership',)
    search_fields = ('first_name', 'last_name', 'middle_name',
                     # 'country', 'region', 'city', 'district',
                     # 'address', 'email',
                     )
    permission_classes = (IsAuthenticated,)
