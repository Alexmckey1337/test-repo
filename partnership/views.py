# -*- coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict

import django_filters
from decimal import Decimal

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Case, IntegerField, DecimalField, Sum, Value, When, Count, BooleanField
from django.db.models import F
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import api_view, list_route, detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from account.models import CustomUser as User, CustomUser
from common.views_mixins import ExportViewSetMixin
from navigation.table_fields import user_table, partner_table
from partnership.permissions import (
    IsSupervisorOrManagerReadOnly, CanCreatePartnerPayment, CanClosePartnerDeal)
from partnership.resources import PartnerResource
from payment.models import Currency
from payment.views_mixins import CreatePaymentMixin, ListPaymentMixin
from .models import Partnership, Deal
from .serializers import (
    DealSerializer, PartnershipSerializer, DealCreateSerializer,
    PartnershipUnregisterUserSerializer, PartnershipForEditSerializer)


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


class PartnershipViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet,
                         CreatePaymentMixin,
                         ListPaymentMixin,
                         ExportViewSetMixin):
    queryset = Partnership.objects.base_queryset().order_by(
        'user__last_name', 'user__first_name', 'user__middle_name')
    serializer_class = PartnershipSerializer
    pagination_class = PartnershipPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('user', 'responsible__user', 'responsible')
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name', 'user__search_name',
                     'user__country', 'user__region', 'user__city', 'user__district',
                     'user__address', 'user__skype', 'user__phone_number', 'user__hierarchy__title',
                     'user__department__title',
                     'user__email',)
    ordering_fields = ('user__first_name', 'user__last_name', 'user__master__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__department__title', 'user__facebook',
                       'user__vkontakte', 'value', 'responsible__user__last_name')
    permission_classes = (IsAuthenticated,)

    payment_list_field = 'extra_payments'
    resource_class = PartnerResource

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

    @list_route(methods=['get'])
    def stats(self, request):
        request_partner_id = request.query_params.get('partner_id')

        current_user = request.user
        current_partner = get_object_or_404(Partnership, user=current_user)

        if current_partner.level > Partnership.MANAGER:
            return Response({'detail': 'Статистику можно просматривать только менеджерам.'},
                            status=status.HTTP_403_FORBIDDEN)
        elif current_partner.level == Partnership.MANAGER or not request_partner_id:
            partnership = current_partner
        else:
            partnership = get_object_or_404(Partnership, id=request_partner_id)

        partners = self._get_partners_list(partnership)

        stat = self._get_partners_stats(partners)

        return Response(stat)

    @list_route(methods=['get'])
    def stats_payments(self, request):
        request_partner_id = request.query_params.get('partner_id')

        current_user = request.user
        current_partner = get_object_or_404(Partnership, user=current_user)

        self.check_stats_permissions(current_partner)

        if current_partner.level == Partnership.MANAGER or not request_partner_id:
            partnership = current_partner
        else:
            partnership = get_object_or_404(Partnership, id=request_partner_id)

        month = self.request.query_params.get('month', timezone.now().month)
        year = self.request.query_params.get('year', timezone.now().year)

        deals = partnership.disciples_deals
        disciples_deals = deals.filter(
            date_created__month=month, date_created__year=year)
        # disciples_deals = Deal.objects.all()  # for test, del this
        deals_annotate = disciples_deals.annotate(
            total_sum=Coalesce(Sum('payments__effective_sum'), Value(0)))

        paid = deals_annotate.filter(total_sum__gte=F('value')).count()
        unpaid = deals_annotate.filter(total_sum__lt=F('value'), total_sum=Decimal(0)).count()
        partial_paid = deals_annotate.filter(total_sum__lt=F('value'), total_sum__gt=Decimal(0)).count()
        result = {
            'sum': {},
            'deals': {
                'paid_count': paid,
                'unpaid_count': unpaid,
                'partial_paid_count': partial_paid
            }
        }

        closed_count = disciples_deals.aggregate(
            closed_count=Sum(
                Case(When(done=True, then=1), default=0,
                     output_field=IntegerField())
            ),
            unclosed_count=Sum(
                Case(When(done=False, then=1), default=0,
                     output_field=IntegerField())
            ))
        result['deals'].update(closed_count)

        paid = set(deals_annotate.filter(total_sum__gte=F('value')).aggregate(p=ArrayAgg('partnership'))['p'])
        unpaid = set(deals_annotate.filter(
            total_sum__lt=F('value'),
            total_sum=Decimal(0)).aggregate(p=ArrayAgg('partnership'))['p'])
        partial_paid = set(deals_annotate.filter(
            total_sum__lt=F('value'),
            total_sum__gt=Decimal(0)).aggregate(p=ArrayAgg('partnership'))['p'])
        paid_count = len(paid - unpaid - partial_paid)
        unpaid_count = len(unpaid - partial_paid - paid)
        partial_paid_count = len(partial_paid | (paid & unpaid))

        closed = set(disciples_deals.filter(done=True).aggregate(p=ArrayAgg('partnership'))['p'])
        unclosed = set(disciples_deals.filter(done=False).aggregate(p=ArrayAgg('partnership'))['p'])
        closed_count = len(closed - unclosed)
        unclosed_count = len(unclosed)

        result['partners'] = {
            'paid_count': paid_count,
            'unpaid_count': unpaid_count,
            'partial_paid_count': partial_paid_count,
            'closed_count': closed_count,
            'unclosed_count': unclosed_count
        }

        currencies = set(
            disciples_deals.aggregate(currency_codes=ArrayAgg('currency__code'))['currency_codes'])

        for c in Currency.objects.filter(code__in=currencies):
            total_paid_sum = deals_annotate.filter(currency=c).aggregate(
                sum_planed=Coalesce(Sum('value'), Value(0)),
                sum_paid=Coalesce(Sum('total_sum'), Value(0)))
            closed_paid_sum = deals_annotate.filter(currency=c, done=True).aggregate(
                sum_planed=Coalesce(Sum('value'), Value(0)),
                sum_paid=Coalesce(Sum('total_sum'), Value(0)))
            result['sum'][c.code] = {
                'currency_name': c.name,
                'total_paid_sum': total_paid_sum,
                'closed_paid_sum': closed_paid_sum
            }

        return Response(result)

    @staticmethod
    def check_stats_permissions(current_partner):
        if current_partner.level > Partnership.MANAGER:
            raise PermissionDenied({'detail': 'Статистику можно просматривать только менеджерам.'})

    @staticmethod
    def _get_partners_stats(partners):
        stat_keys = ('total_deals', 'paid_deals', 'unpaid_deals',
                     'sum_deals', 'value',
                     'paid_sum_deals', 'unpaid_sum_deals')
        stat = {}
        for k in stat_keys:
            if k == 'value':
                stat['planned_sum_deals'] = sum([p[k] for p in partners])
            else:
                stat[k] = sum([p[k] for p in partners])

        stat['count_partners'] = len(partners)
        stat['paid_partners'] = len([1 for i in partners if i['is_paid']])
        stat['partial_paid_partners'] = len(
            list(filter(lambda x: x > 0, [p['paid_deals'] for p in partners if not p['is_paid']])))
        stat['unpaid_partners'] = len(partners) - stat['paid_partners'] - stat['partial_paid_partners']

        stat['partners'] = [p for p in partners if p['total_deals'] > 0]

        return stat

    def _get_partners_list(self, partnership):

        month = self.request.query_params.get('month', timezone.now().month)
        year = self.request.query_params.get('year', timezone.now().year)
        partners = list(partnership.disciples.annotate(
            total_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          then=1), default=0,
                     output_field=IntegerField())
            ),
            paid_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          deals__done=True, then=1), default=0,
                     output_field=IntegerField())
            ),
            unpaid_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          deals__done=False, then=1), default=0,
                     output_field=IntegerField())
            ),
            sum_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          then='deals__value'), default=0,
                     output_field=DecimalField())
            ),
            paid_sum_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          deals__done=True, then='deals__value'), default=0,
                     output_field=DecimalField())
            ),
            unpaid_sum_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          deals__done=False, then='deals__value'), default=0,
                     output_field=DecimalField())
            ),
            partner_name=Concat('user__last_name', Value(' '), 'user__first_name', Value(' '), 'user__middle_name')
        ).values('partner_name',
                 'total_deals', 'paid_deals', 'unpaid_deals',
                 'sum_deals', 'value',
                 'paid_sum_deals', 'unpaid_sum_deals'))

        for p in partners:
            p['is_paid'] = bool(p['paid_sum_deals']) and p['paid_sum_deals'] >= p['value']

        return partners


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
    permission_classes = (IsSupervisorOrManagerReadOnly,)

    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_create_class
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        if Partnership.objects.get(user=user).level < Partnership.MANAGER:
            return self.queryset
        return self.queryset.filter(partnership__responsible__user=user)


@api_view(['POST'])
def create_partnership(request):
    '''POST: (user, responsible, value)'''

    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        user_id = data['user']
        responsible_partnership_id = None
        if 'responsible' in data.keys():
            responsible_partnership_id = data['responsible']
        value = data['value']
        date = data['date']
        try:
            Partnership.objects.get(user__id=user_id)
            response_dict['message'] = "Этот пользователь уже имеет партнерство."
            response_dict['status'] = False
        except Partnership.DoesNotExist:
            try:
                user = User.objects.get(id=user_id)
                responsible_partnership = Partnership.objects.filter(id=responsible_partnership_id).first()
                object = Partnership.objects.create(user=user, responsible=responsible_partnership, value=value,
                                                    date=date)
                if object:
                    serializer = PartnershipSerializer(object, context={'request': request})
                    response_dict['data'] = serializer.data
                    response_dict['message'] = "Партнерство успешно добавлено."
                    response_dict['status'] = True
            except User.DoesNotExist:
                response_dict['data'] = []
                response_dict['message'] = "Пользователя не существует."
                response_dict['status'] = False
    return Response(response_dict)


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
