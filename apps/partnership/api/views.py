# -*- coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Sum, When, Case, F, IntegerField, Q, Subquery
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import exceptions, filters, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404, DestroyAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from apps.account.models import CustomUser
from apps.analytics.decorators import log_perform_create, log_perform_update
from apps.analytics.mixins import LogAndCreateUpdateDestroyMixin
from apps.payment.models import Payment
from common.filters import FieldSearchFilter
from common.views_mixins import ModelWithoutDeleteViewSet
from apps.group.api.filters import FilterChurchPartnerMasterTree
from apps.partnership.api.filters import (
    FilterByPartnerBirthday, DealDateAndValueFilter, FilterPartnerMasterTreeWithSelf,
    PartnerUserFilter, DealFilterByPaymentStatus, PartnerFilterByDateAge,
    ChurchDateAndValueFilter, ChurchPartnerFilter, LastDealFilter, LastChurchDealFilter,
    PartnerFilterByLevel)
from apps.partnership.api.mixins import (
    PartnerStatMixin, DealCreatePaymentMixin, DealListPaymentMixin,
    PartnerExportViewSetMixin, PartnerStatusReviewMixin, StatsSummaryMixin,
    ChurchDealListPaymentMixin)
from apps.partnership.api.pagination import PartnershipPagination, DealPagination, DealDuplicatePagination, \
    ChurchDealPagination, \
    LastPaymentPagination, LastDealPagination, ChurchPartnerPagination
from apps.partnership.api.permissions import (
    CanSeeDeals, CanSeePartners, CanCreateDeals, CanUpdateDeals,
    CanUpdatePartner, CanUpdateManagersPlan, CanCreateUpdatePartnerGroup,
    CanSeePartnerGroups, CanCreatePartnerRole, CanDeletePartnerRole, CanUpdatePartnerRole, CanUpdateChurchDeals,
    CanUpdateChurchPartner,
    CanSeeChurchPartners, CanCreateChurchDeals, CanSeeChurchDeals)
from apps.partnership.api.serializers import (
    DealSerializer, PartnershipUpdateSerializer, DealCreateSerializer,
    PartnershipTableSerializer, DealUpdateSerializer,
    PartnershipCreateSerializer, PartnershipSerializer, PartnerGroupSerializer,
    ChurchPartnerSerializer, ChurchDealUpdateSerializer, ChurchPartnerTableSerializer, ChurchDealCreateSerializer,
    ChurchDealSerializer,
    ChurchPartnerCreateSerializer, ChurchPartnerUpdateSerializer,
    PartnerRoleSerializer, CreatePartnerRoleSerializer, DealDuplicateSerializer, LastDealSerializer,
    LastDealPaymentSerializer, LastChurchDealSerializer, LastChurchDealPaymentSerializer, ChurchDealDuplicateSerializer)
from apps.partnership.models import Partnership, Deal, PartnershipLogs, PartnerRoleLog, PartnerGroup, PartnerRole, \
    ChurchPartner, \
    ChurchPartnerLog, ChurchDeal
from apps.partnership.resources import PartnerResource, ChurchPartnerResource


class PartnershipViewSet(
    LogAndCreateUpdateDestroyMixin,
    ModelWithoutDeleteViewSet,
    PartnerExportViewSetMixin,
    PartnerStatMixin,
    StatsSummaryMixin
):
    queryset = Partnership.objects.base_queryset().order_by(
        'user__last_name', 'user__first_name', 'user__middle_name')
    serializer_class = PartnershipSerializer
    serializer_update_class = PartnershipUpdateSerializer
    serializer_create_class = PartnershipCreateSerializer
    serializer_read_class = PartnershipTableSerializer
    pagination_class = PartnershipPagination
    filter_backends = (rest_framework.DjangoFilterBackend,
                       FieldSearchFilter,
                       FilterByPartnerBirthday,
                       FilterPartnerMasterTreeWithSelf,
                       PartnerFilterByDateAge,
                       PartnerFilterByLevel,
                       filters.OrderingFilter,)
    filter_fields = ('user', 'responsible')
    ordering_fields = ('user__first_name', 'user__last_name', 'user__master__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__facebook',
                       'user__vkontakte', 'value', 'responsible__last_name', 'group', 'group__title',
                       'user__department',)
    field_search_fields = {
        'search_fio': ('user__last_name', 'user__first_name', 'user__middle_name', 'user__search_name'),
        'search_email': ('user__email',),
        'search_phone_number': ('user__phone_number',),
        'search_country': ('user__country',),
        'search_city': ('user__city',),
    }
    permission_classes = (IsAuthenticated,)
    permission_update_classes = (IsAuthenticated, CanUpdatePartner)
    permission_list_classes = (IsAuthenticated, CanSeePartners)
    filter_class = PartnerUserFilter

    payment_list_field = 'extra_payments'
    resource_class = PartnerResource

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return self.serializer_read_class
        if self.action in ('update', 'partial_update'):
            return self.serializer_update_class
        if self.action in ('create',):
            return self.serializer_create_class
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.for_user(user=self.request.user)

    @log_perform_update
    def perform_update(self, serializer, **kwargs):
        partner = kwargs.get('new_obj')
        PartnershipLogs.log_partner(partner)
        return partner

    @log_perform_create
    def perform_create(self, serializer, **kwargs):
        partner = kwargs.get('new_obj')
        PartnershipLogs.log_partner(partner)
        return partner

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permission() for permission in self.permission_list_classes]
        if self.action in ('update', 'partial_update'):
            return [permission() for permission in self.permission_update_classes]
        return super(PartnershipViewSet, self).get_permissions()

    # TODO deprecated
    @detail_route(methods=['put'], permission_classes=(IsAuthenticated, CanUpdatePartner))
    def update_need(self, request, pk=None):
        """
        Update the text of the partner's needs.

        :param request: rest_framework.Request
        :param pk: id of partner
        :return: dict with need_text, e.g. {'need_text': 'i am update text'}
        """
        if not request.user.can_update_partner_need:
            raise exceptions.PermissionDenied(detail=_(
                'You do not have permission to update need of this partner.'))
        text = request.data.get('need_text', None)
        if text is None:
            return Response({'detail': _("'need_text' is required field.")},
                            status=status.HTTP_400_BAD_REQUEST)
        partnership = self.get_object()
        partnership.need_text = text
        partnership.save()

        return Response({'need_text': text})

    @detail_route(methods=['POST'], permission_classes=(CanUpdateManagersPlan,))
    def set_plan(self, request, pk):
        manager = get_object_or_404(CustomUser, pk=pk)
        plan_sum = request.data.get('plan_sum')
        if not plan_sum:
            raise exceptions.ValidationError({'message': _('Parameter {plan_sum} not passed')})
        try:
            plan_sum = Decimal(plan_sum)
        except Exception as e:
            print(e)
            raise exceptions.ValidationError({'message': _('Parameter {plan_sum} must be Integer')})

        if not getattr(manager, 'partner_role', None):
            raise exceptions.ValidationError({'message': _('User is not a manager')})
        manager.partner_role.plan = plan_sum
        manager.partner_role.save()
        PartnerRoleLog.log_partner_role(manager.partner_role)

        return Response({'message': 'План менеджера успешно установлен в %s' % manager.partner_role.plan})


class ChurchPartnerViewSet(
    LogAndCreateUpdateDestroyMixin,
    ModelWithoutDeleteViewSet,
    PartnerExportViewSetMixin,
):
    queryset = ChurchPartner.objects.select_related('church')
    pagination_class = ChurchPartnerPagination

    serializer_class = ChurchPartnerSerializer
    serializer_update_class = ChurchPartnerUpdateSerializer
    serializer_create_class = ChurchPartnerCreateSerializer
    serializer_read_class = ChurchPartnerTableSerializer

    permission_classes = (IsAuthenticated,)
    permission_update_classes = (IsAuthenticated, CanUpdateChurchPartner)
    permission_list_classes = (IsAuthenticated, CanSeeChurchPartners)

    filter_backends = (rest_framework.DjangoFilterBackend,
                       FieldSearchFilter,
                       PartnerFilterByDateAge,
                       FilterChurchPartnerMasterTree,
                       filters.OrderingFilter,)
    filter_class = ChurchPartnerFilter
    ordering_fields = ('church__title', 'church__city', 'church__department__title', 'church__home_group',
                       'church__is_open', 'church__opening_date', 'church__pastor__last_name', 'church__phone_number',
                       'church__address', 'church__website', 'church__country',
                       'value', 'responsible__last_name', 'group', 'group__title')
    field_search_fields = {
        'search_fio': ('church__title',),
        'search_address': ('church__address',),
        'search_website': ('church__website',),
        'search_phone': ('church__phone_number',),
        'search_country': ('church__country',),
        'search_city': ('church__city',),
    }

    resource_class = ChurchPartnerResource

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return self.serializer_read_class
        if self.action in ('update', 'partial_update'):
            return self.serializer_update_class
        if self.action in ('create',):
            return self.serializer_create_class
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permission() for permission in self.permission_list_classes]
        if self.action in ('update', 'partial_update'):
            return [permission() for permission in self.permission_update_classes]
        return super().get_permissions()

    @log_perform_create
    def perform_create(self, serializer, **kwargs):
        partner = kwargs.get('new_obj')
        ChurchPartnerLog.log_partner(partner)
        return partner

    @log_perform_update
    def perform_update(self, serializer, **kwargs):
        partner = kwargs.get('new_obj')
        ChurchPartnerLog.log_partner(partner)
        return partner


class LastChurchPartnerDealsView(GenericAPIView):
    pagination_class = LastDealPagination
    serializer_class = LastChurchDealSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filter_class = LastChurchDealFilter
    # filter_fields = ('done',)
    permission_classes = (IsAuthenticated,)

    partner = None
    # TODO delete
    action = 'list'

    def get(self, request, *args, **kwargs):
        """
        Getting last deals of church partner


        By default ordering by ``-date_created``.
        Pagination by 10 deals per page.
        """
        self.partner = get_object_or_404(ChurchPartner, pk=kwargs.get('partner_id'))

        deals = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(deals)
        serializer = self.get_serializer(page, many=True)
        return Response(data={'results': serializer.data})

    def get_queryset(self):
        return self.partner.deals.select_related('responsible').annotate_responsible_name().annotate(
            total_payments=Sum('payments__effective_sum')).order_by('-date_created')


class LastChurchPartnerPaymentsView(GenericAPIView):
    queryset = Payment.objects.all()
    pagination_class = LastPaymentPagination
    serializer_class = LastChurchDealPaymentSerializer
    permission_classes = (IsAuthenticated,)

    partner = None

    def get(self, request, *args, **kwargs):
        """
        Getting last payments of church partner


        By default ordering by ``-created_at``.
        Pagination by 10 payments per page.
        """
        self.partner = get_object_or_404(ChurchPartner, pk=kwargs.get('partner_id'))

        payments = self.get_queryset()
        page = self.paginate_queryset(payments)
        serializer = self.get_serializer(page, many=True)
        return Response(data={'results': serializer.data})

    def get_queryset(self):
        deals = self.get_deals()
        return self.queryset.select_related('manager').order_by('-created_at').filter(
            (Q(content_type__model='churchdeal') & Q(object_id__in=Subquery(deals.values('pk'))))
        ).extra(
            select={
                'deal_date': '''
                    SELECT
                    partnership_churchdeal.date_created AS purpose_date
                    FROM partnership_churchdeal

                    WHERE partnership_churchdeal.id = payment_payment.object_id'''
            })

    def get_deals(self):
        return self.partner.deals.order_by()


class LastPartnerDealsView(GenericAPIView):
    pagination_class = LastDealPagination
    serializer_class = LastDealSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filter_class = LastDealFilter
    # filter_fields = ('done',)
    permission_classes = (IsAuthenticated,)

    partner = None
    # TODO delete
    action = 'list'

    def get(self, request, *args, **kwargs):
        """
        Getting last deals of partner


        By default ordering by ``-date_created``.
        Pagination by 10 deals per page.
        """
        self.partner = get_object_or_404(Partnership, pk=kwargs.get('partner_id'))

        deals = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(deals)
        serializer = self.get_serializer(page, many=True)
        return Response(data={'results': serializer.data})

    def get_queryset(self):
        return self.partner.deals.select_related('responsible').annotate_responsible_name().annotate(
            total_payments=Sum('payments__effective_sum')).order_by('-date_created')


class LastPartnerPaymentsView(GenericAPIView):
    queryset = Payment.objects.all()
    pagination_class = LastPaymentPagination
    serializer_class = LastDealPaymentSerializer
    permission_classes = (IsAuthenticated,)

    partner = None

    def get(self, request, *args, **kwargs):
        """
        Getting last payments of partner


        By default ordering by ``-created_at``.
        Pagination by 10 payments per page.
        """
        self.partner = get_object_or_404(Partnership, pk=kwargs.get('partner_id'))

        payments = self.get_queryset()
        page = self.paginate_queryset(payments)
        serializer = self.get_serializer(page, many=True)
        return Response(data={'results': serializer.data})

    def get_queryset(self):
        deals = self.get_deals()
        return self.queryset.select_related('manager').order_by('-created_at').filter(
            (Q(content_type__model='deal') & Q(object_id__in=Subquery(deals.values('pk'))))
        ).extra(
            select={
                'deal_date': '''
                    SELECT
                    partnership_deal.date_created AS purpose_date
                    FROM partnership_deal

                    WHERE partnership_deal.id = payment_payment.object_id'''
            })

    def get_deals(self):
        return self.partner.deals.order_by()


class PartnerGroupViewSet(ModelWithoutDeleteViewSet):
    queryset = PartnerGroup.objects.order_by('title')
    serializer_class = PartnerGroupSerializer
    filter_backends = (filters.SearchFilter, rest_framework.DjangoFilterBackend)
    search_fields = ('title',)
    filter_fields = ('type',)
    permission_classes = (IsAdminUser,)
    permission_create_update_classes = (IsAuthenticated, CanCreateUpdatePartnerGroup)
    permission_list_classes = (IsAuthenticated, CanSeePartnerGroups)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permission() for permission in self.permission_list_classes]
        if self.action in ('update', 'partial_update', 'create'):
            return [permission() for permission in self.permission_create_update_classes]
        return super().get_permissions()


class DealViewSet(LogAndCreateUpdateDestroyMixin, ModelViewSet, DealCreatePaymentMixin,
                  DealListPaymentMixin, PartnerStatusReviewMixin):
    queryset = Deal.objects.base_queryset(). \
        annotate_full_name(). \
        annotate_responsible_name(). \
        annotate_total_sum(). \
        order_by('-date_created', 'id')
    serializer_class = DealSerializer
    serializer_create_class = DealCreateSerializer
    serializer_update_class = DealUpdateSerializer
    pagination_class = DealPagination
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       DealFilterByPaymentStatus,)
    ordering_fields = ('value',
                       'responsible__last_name',
                       'partnership__user__last_name',
                       'date_created',
                       'done', 'type')
    filter_class = DealDateAndValueFilter
    search_fields = ('partnership__user__first_name',
                     'partnership__user__last_name',
                     'partnership__user__search_name',
                     'partnership__user__middle_name',)
    permission_classes = (IsAuthenticated, CanSeeDeals)
    permission_list_classes = (IsAuthenticated, CanSeeDeals)
    permission_create_classes = (IsAuthenticated, CanCreateDeals)
    permission_update_classes = (IsAuthenticated, CanUpdateDeals)

    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_create_class
        if self.action in ('update', 'partial_update'):
            return self.serializer_update_class
        return self.serializer_class

    def get_queryset(self):
        """
        payment_status = 0, it's a deal with payments total sum = 0;
        payment_status = 1, it's a deal with partial paid;
        payment_status = 2, it's a deal with full paid;
        """
        return self.queryset.for_user(self.request.user).annotate(
            total_payments=Sum('payments__effective_sum')).annotate(
            payment_status=Case(
                When(Q(total_payments__lt=F('value')) & Q(total_payments__gt=0), then=1),
                When(total_payments__gte=F('value'), then=2),
                default=0, output_field=IntegerField())
        )

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permission() for permission in self.permission_list_classes]
        if self.action == 'create':
            return [permission() for permission in self.permission_create_classes]
        if self.action in ('update', 'partial_update'):
            return [permission() for permission in self.permission_update_classes]
        return super(DealViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):
        try:
            partner = Partnership.objects.get(id=request.data.get('partnership'))
        except ObjectDoesNotExist:
            raise exceptions.ValidationError(detail=_('Partner does not exist.'))
        if not request.user.can_create_deal_for_partner(partner):
            raise exceptions.PermissionDenied(detail=_(
                'You do not have permission to create deal for this partner.'))

        return super().create(request, *args, **kwargs)

    @log_perform_update
    def perform_update(self, serializer, **kwargs):
        deal = kwargs.get('new_obj')
        self.partnership_status_review(self.get_object().partnership)

        return deal

    @list_route(methods=['GET'],
                serializer_class=DealDuplicateSerializer,
                pagination_class=DealDuplicatePagination, )
    def check_duplicates(self, request):
        data = request.query_params
        if data.get('date_created') and data.get('value') and data.get('partnership_id'):
            date_created = data.get('date_created')
            value = data.get('value')
            partnership_id = data.get('partnership_id')
            try:
                year = date_created.split('-')[0]
                month = date_created.split('-')[1]
            except IndexError:
                return Response({'message': 'Param {date_created} must be in "YYYY-MM-DD" format'})
        else:
            return Response({'message': 'Not all parameters have been transferred. '
                                        'Params {date_created}, {value}, {partnership} must be passed'})

        deals = self.queryset.filter(partnership_id=partnership_id,
                                     date_created__month=month,
                                     date_created__year=year,
                                     value=value)
        if not deals:
            return Response({'message': 'Duplicates are not detected'})

        page = self.paginate_queryset(deals)
        if page is not None:
            deals = self.get_serializer(page, many=True)
            return self.get_paginated_response(deals.data)

        deals = self.serializer_class(deals, many=True)
        return Response(deals.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_duplicates(self, request):
        deal_ids = self.filter_queryset(self.queryset).values_list('id', flat=True)
        if not deal_ids:
            return Response(list(), status.HTTP_200_OK)

        query = """
                SELECT
                array_agg(d.id) c,
                p.id,
                CONCAT(auth_user.last_name, ' ', auth_user.first_name, ' ', account_customuser.middle_name),
                d.value,
                to_char(d.date_created, 'YYYY.MM')
                FROM partnership_deal d
                JOIN partnership_partnership p ON d.partnership_id = p.id
                JOIN account_customuser ON p.user_id = account_customuser.user_ptr_id
                JOIN auth_user ON account_customuser.user_ptr_id = auth_user.id
                WHERE d.id in ('{0}')
                GROUP BY p.id, d.value, to_char(d.date_created, 'YYYY.MM'),
                CONCAT(auth_user.last_name, ' ', auth_user.first_name, ' ', account_customuser.middle_name)
                HAVING count(*) > 1
                ORDER BY p.id;
            """.format("','".join(["%s"] * len(deal_ids)))

        with connection.cursor() as cursor:
            cursor.execute(query, deal_ids)
            data = cursor.fetchall()

        page = int(request.query_params.get('page', 1) or 1)

        try:
            page_data = data[page - 1]
        except IndexError:
            raise exceptions.ValidationError(
                {'message': _('Parameter {page} out of array range')}
            )

        deals_data = {
            'deal_ids': page_data[0],
            'partnership_id': page_data[1],
            'partnership_fio': page_data[2],
            'value': page_data[3],
            'date_created': page_data[4],
            'count': len(data)
        }

        deals_with_payment = Deal.objects.filter(id__in=deals_data.get('deal_ids')).annotate(
            payment_sum=Sum('payments__effective_sum')).values('id', 'payment_sum')

        deals_data['deal_ids'] = deals_with_payment

        return Response(deals_data, status=status.HTTP_200_OK)


# class AllDealListView(GenericAPIView):
#     user_queryset = Deal.objects.base_queryset(). \
#         annotate_full_name(). \
#         annotate_responsible_name(). \
#         annotate_total_sum()
#     church_queryset = ChurchDeal.objects.base_queryset(). \
#         annotate_full_name(). \
#         annotate_responsible_name(). \
#         annotate_total_sum()
#
#     pagination_class = DealPagination
#     filter_backends = (rest_framework.DjangoFilterBackend,
#                        DealFilterByPaymentStatus,)
#     user_filter_backends = (filters.SearchFilter,)
#     church_filter_backends = (filters.SearchFilter,)
#     filter_class = DateAndValueFilter
#     serializer_class = AllDealSerializer
#
#     ordering_fields = ('value',
#                        'responsible__last_name',
#                        'partnership__user__last_name',
#                        'date_created',
#                        'done', 'type')
#
#     search_fields = ('partnership__user__first_name',
#                      'partnership__user__last_name',
#                      'partnership__user__search_name',
#                      'partnership__user__middle_name',)
#     order_backend = filters.OrderingFilter
#     permission_classes = (IsAuthenticated, CanSeeDeals)
#
#     def get_user_queryset(self):
#         return self.user_queryset
#
#     def get_church_queryset(self):
#         return self.church_queryset
#
#     def get(self, request, *args, **kwargs):
#         print(self.user_queryset.query)
#         user_qs, church_qs = self.filter_querysets(self.get_user_queryset(), self.get_church_queryset())
#
#         # fields = ('id', 'value', 'date', 'date_created', 'done', 'expired',
#         #           'description', 'full_name', 'total_sum', 'responsible_name')
#         qs = user_qs.union(church_qs)
#         if request.query_params.get('ordering'):
#             qs = self.order_backend().filter_queryset(self.request, qs, self)
#         else:
#             qs = qs.order_by('-date_created')
#         page = self.paginate_queryset(qs)
#         serializer = self.get_serializer(page, many=True)
#         return self.get_paginated_response(serializer.data)
#
#     def filter_querysets(self, user_qs, church_qs):
#         # for backend in list(self.filter_backends):
#         #     user_qs = backend().filter_queryset(self.request, user_qs, self)
#         #     church_qs = backend().filter_queryset(self.request, church_qs, self)
#         # for backend in list(self.user_filter_backends):
#         #     user_qs = backend().filter_queryset(self.request, user_qs, self)
#         # for backend in list(self.church_filter_backends):
#         #     church_qs = backend().filter_queryset(self.request, church_qs, self)
#         return user_qs, church_qs


class ChurchDealViewSet(LogAndCreateUpdateDestroyMixin, ModelWithoutDeleteViewSet,
                        DealCreatePaymentMixin, ChurchDealListPaymentMixin, PartnerStatusReviewMixin):
    queryset = ChurchDeal.objects.base_queryset(). \
        annotate_full_name(). \
        annotate_responsible_name(). \
        annotate_total_sum()

    serializer_class = ChurchDealSerializer
    serializer_create_class = ChurchDealCreateSerializer
    serializer_update_class = ChurchDealUpdateSerializer
    pagination_class = ChurchDealPagination
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       DealFilterByPaymentStatus,)
    ordering_fields = ('value',
                       'responsible__last_name',
                       'partnership__church__title',
                       'date_created',
                       'done', 'type')
    filter_class = ChurchDateAndValueFilter
    search_fields = ('partnership__church__title',)

    permission_classes = (IsAuthenticated, CanSeeChurchDeals)
    permission_list_classes = (IsAuthenticated, CanSeeChurchDeals)
    permission_create_classes = (IsAuthenticated, CanCreateChurchDeals)
    permission_update_classes = (IsAuthenticated, CanUpdateChurchDeals)

    def get_queryset(self):
        """
        payment_status = 0, it's a deal with payments total sum = 0;
        payment_status = 1, it's a deal with partial paid;
        payment_status = 2, it's a deal with full paid;
        """
        return self.queryset.for_user(self.request.user).annotate(
            total_payments=Sum('payments__effective_sum')).annotate(
            payment_status=Case(
                When(Q(total_payments__lt=F('value')) & Q(total_payments__gt=0), then=1),
                When(total_payments__gte=F('value'), then=2),
                default=0, output_field=IntegerField())
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_create_class
        if self.action in ('update', 'partial_update'):
            return self.serializer_update_class
        return self.serializer_class

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permission() for permission in self.permission_list_classes]
        if self.action == 'create':
            return [permission() for permission in self.permission_create_classes]
        if self.action in ('update', 'partial_update'):
            return [permission() for permission in self.permission_update_classes]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        try:
            partner = ChurchPartner.objects.get(id=request.data.get('partnership'))
        except ObjectDoesNotExist:
            raise exceptions.ValidationError(detail=_('Partner does not exist.'))
        if not request.user.can_create_church_deal_for_partner(partner):
            raise exceptions.PermissionDenied(detail=_(
                'You do not have permission to create deal for this partner.'))

        return super().create(request, *args, **kwargs)

    @log_perform_update
    def perform_update(self, serializer, **kwargs):
        church_deal = kwargs.get('new_obj')
        self.partnership_status_review(self.get_object().partnership)

        return church_deal

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.payments.all().exists() and not request.data.get('force'):
            raise exceptions.ValidationError(
                {'message': _('Данная сделка содержит платежи. '
                              'Удаление сделки повлечет за собой удаление всех связанных с ней платежей.')})

        self.perform_destroy(instance)
        return Response({'message': 'Сделка успещно удалена.'}, status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['GET'],
                serializer_class=ChurchDealDuplicateSerializer,
                pagination_class=DealDuplicatePagination, )
    def check_duplicates(self, request):
        data = request.query_params
        if data.get('date_created') and data.get('value') and data.get('partnership_id'):
            date_created = data.get('date_created')
            value = data.get('value')
            partnership_id = data.get('partnership_id')
            try:
                year, month, *_ = date_created.split('-')
            except IndexError:
                return Response({'message': 'Param {date_created} must be in "YYYY-MM-DD" format'})
        else:
            return Response({'message': 'Not all parameters have been transferred. '
                                        'Params {date_created}, {value}, {partnership} must be passed'})

        deals = self.queryset.filter(partnership_id=partnership_id,
                                     date_created__month=month,
                                     date_created__year=year,
                                     value=value)
        if not deals:
            return Response({'message': 'Duplicates are not detected'})

        page = self.paginate_queryset(deals)
        if page is not None:
            deals = self.get_serializer(page, many=True)
            return self.get_paginated_response(deals.data)

        deals = self.serializer_class(deals, many=True)
        return Response(deals.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'],
                serializer_class=ChurchDealDuplicateSerializer,
                pagination_class=DealDuplicatePagination, )
    def get_duplicates(self, request):
        query = """
                SELECT
                array_agg(d.id) c,
                p.id,
                d.value,
                to_char(d.date_created, 'YYYY.MM')
                FROM partnership_churchdeal d
                JOIN partnership_churchpartner p ON d.partnership_id = p.id
                GROUP BY p.id, d.value, to_char(d.date_created, 'YYYY.MM')
                HAVING count(*) > 1
                ORDER BY count(*) DESC;
            """

        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()

        deal_ids = []
        for ids, *_ in data:
            deal_ids.extend(ids)

        deals = self.queryset.filter(id__in=deal_ids).order_by('partnership_id')

        page = self.paginate_queryset(deals)
        if page is not None:
            deals = self.get_serializer(page, many=True)
            return self.get_paginated_response(deals.data)

        deals = self.serializer_class(deals, many=True)
        return Response(deals.data, status=status.HTTP_200_OK)


class CheckPartnerLevelMixin:
    def check_partner_level(self, serializer):
        if (not self.request.user.has_partner_role or
                serializer.initial_data.get('level') < self.request.user.partner_role.level):
            raise ValidationError({'detail': _('Вы не можете назначать пользователям уровень выше вашего.')})


class SetPartnerRoleView(CheckPartnerLevelMixin, GenericAPIView):
    queryset = PartnerRole.objects.all()
    serializer_class = CreatePartnerRoleSerializer
    permission_classes = (IsAuthenticated, CanCreatePartnerRole)
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = kwargs.get('user_id')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = self.user
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        self.check_partner_level(serializer)
        partner_role = serializer.save()
        PartnerRoleLog.log_partner_role(partner_role)

    def get_success_headers(self, data):
        try:
            return {'Location': data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}


class DeletePartnerRoleView(DestroyAPIView):
    queryset = PartnerRole.objects.all()
    serializer_class = PartnerRoleSerializer
    permission_classes = (IsAuthenticated, CanDeletePartnerRole)

    lookup_field = 'user_id'

    def perform_destroy(self, instance):
        if Partnership.objects.filter(responsible=instance.user).exists():
            raise ValidationError({'detail': _('Пользователь является ответственным по партнерам')})
        PartnerRoleLog.delete_partner_role(instance)
        instance.delete()


class UpdatePartnerRoleView(CheckPartnerLevelMixin, UpdateAPIView):
    queryset = PartnerRole.objects.all()
    serializer_class = PartnerRoleSerializer
    permission_classes = (IsAuthenticated, CanUpdatePartnerRole)

    lookup_field = 'user_id'

    def perform_update(self, serializer):
        self.check_partner_level(serializer)
        partner_role = serializer.save()
        PartnerRoleLog.log_partner_role(partner_role)
