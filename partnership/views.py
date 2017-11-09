# -*- coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, When, Case, F, IntegerField, Q
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import exceptions, filters, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.generics import get_object_or_404, DestroyAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError

from account.models import CustomUser
from analytics.decorators import log_perform_create, log_perform_update
from analytics.mixins import LogAndCreateUpdateDestroyMixin
from common.filters import FieldSearchFilter
from common.views_mixins import ModelWithoutDeleteViewSet
from partnership.filters import (FilterByPartnerBirthday, DateAndValueFilter, FilterPartnerMasterTreeWithSelf,
                                 PartnerUserFilter, DealFilterByPaymentStatus, PartnerFilterByDateAge)
from partnership.mixins import (PartnerStatMixin, DealCreatePaymentMixin, DealListPaymentMixin,
                                PartnerExportViewSetMixin, PartnerStatusReviewMixin, ManagerSummaryMixin)
from partnership.pagination import PartnershipPagination, DealPagination, DealDuplicatePagination
from partnership.permissions import (CanSeeDeals, CanSeePartners, CanCreateDeals, CanUpdateDeals,
                                     CanUpdatePartner, CanUpdateManagersPlan, CanCreateUpdatePartnerGroup,
                                     CanSeePartnerGroups, CanCreatePartnerRole, CanDeletePartnerRole,
                                     CanUpdatePartnerRole)
from partnership.resources import PartnerResource
from .models import Partnership, Deal, PartnershipLogs, PartnerRoleLog, PartnerGroup, PartnerRole
from .serializers import (DealSerializer, PartnershipUpdateSerializer, DealCreateSerializer,
                          PartnershipTableSerializer, DealUpdateSerializer,
                          PartnershipCreateSerializer, PartnershipSerializer, PartnerGroupSerializer,
                          PartnerRoleSerializer, CreatePartnerRoleSerializer, DealDuplicateSerializer)
from django.db import connection
from datetime import datetime
import time


class PartnershipViewSet(
    LogAndCreateUpdateDestroyMixin,
    ModelWithoutDeleteViewSet,
    PartnerExportViewSetMixin,
    PartnerStatMixin,
    ManagerSummaryMixin
):
    queryset = Partnership.objects.base_queryset().order_by(
        'user__last_name', 'user__first_name', 'user__middle_name')
    serializer_class = PartnershipSerializer
    serializer_update_class = PartnershipUpdateSerializer
    serializer_create_class = PartnershipCreateSerializer
    serializer_read_class = PartnershipTableSerializer
    pagination_class = PartnershipPagination
    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       FilterByPartnerBirthday,
                       FilterPartnerMasterTreeWithSelf,
                       PartnerFilterByDateAge,
                       filters.OrderingFilter,)
    filter_fields = ('user', 'responsible')
    ordering_fields = ('user__first_name', 'user__last_name', 'user__master__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__facebook',
                       'user__vkontakte', 'value', 'responsible__last_name', 'group', 'group__title')
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
        partner = serializer.save()
        PartnershipLogs.log_partner(partner)

    @log_perform_create
    def perform_create(self, serializer, **kwargs):
        partner = serializer.save()
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


class PartnerGroupViewSet(ModelWithoutDeleteViewSet):
    queryset = PartnerGroup.objects.order_by('title')
    serializer_class = PartnerGroupSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title',)
    permission_classes = (IsAdminUser,)
    permission_create_update_classes = (IsAuthenticated, CanCreateUpdatePartnerGroup)
    permission_list_classes = (IsAuthenticated, CanSeePartnerGroups)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permission() for permission in self.permission_list_classes]
        if self.action in ('update', 'partial_update', 'create'):
            return [permission() for permission in self.permission_create_update_classes]
        return super().get_permissions()


class DealViewSet(LogAndCreateUpdateDestroyMixin, ModelWithoutDeleteViewSet, DealCreatePaymentMixin,
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
    filter_class = DateAndValueFilter
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

        return super(DealViewSet, self).create(request, *args, **kwargs)

    def perform_update(self, serializer, **kwargs):
        response = super(LogAndCreateUpdateDestroyMixin, self).perform_create(serializer, **kwargs)
        self.partnership_status_review(self.get_object().partnership)

        return response

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
        deals = self.filter_queryset(self.queryset).values_list('id', flat=True)

        query = """
                SELECT
                array_agg(d.id) c,
                p.id,
                CONCAT(auth_user.last_name, ' ', auth_user.first_name, ' ', account_customuser.middle_name),
                d.value,
                to_char(d.date_created, 'YYYY.MM')
                FROM partnership_deal d
                JOIN partnership_partnership p on d.partnership_id = p.id
                JOIN account_customuser ON p.user_id = account_customuser.user_ptr_id
                JOIN auth_user ON account_customuser.user_ptr_id = auth_user.id
                WHERE d.id in ('{0}')
                GROUP BY p.id, d.value, to_char(d.date_created, 'YYYY.MM'),
                CONCAT(auth_user.last_name, ' ', auth_user.first_name, ' ', account_customuser.middle_name)
                HAVING count(*) > 1
                ORDER BY count(*) DESC;
            """.format("','".join(str(x) for x in deals))

        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()

        for x in enumerate(data):
            data[x[0]] = {
                'deal_ids': x[1][0],
                'partnership_id': x[1][1],
                'partnership_fio': x[1][2],
                'value': x[1][3],
                'date_created': x[1][4]
            }

        return Response(data, status=status.HTTP_200_OK)


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
