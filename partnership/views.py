# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import (Sum, When, Case, F, IntegerField, Q, DecimalField, OuterRef,
                              Subquery, Count, Value as V)
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import exceptions, filters, mixins, status, viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from analytics.mixins import LogAndCreateUpdateDestroyMixin
from common.filters import FieldSearchFilter
from common.views_mixins import ModelWithoutDeleteViewSet
from navigation.table_fields import partnership_summary_table
from partnership.filters import (FilterByPartnerBirthday, DateAndValueFilter, FilterPartnerMasterTreeWithSelf,
                                 PartnerUserFilter, DealFilterByPaymentStatus)
from partnership.mixins import (PartnerStatMixin, DealCreatePaymentMixin, DealListPaymentMixin,
                                PartnerExportViewSetMixin, PartnerStatusReviewMixin)
from partnership.pagination import PartnershipPagination, DealPagination
from partnership.permissions import (CanSeeDeals, CanSeePartners, CanCreateDeals, CanUpdateDeals,
                                     CanUpdatePartner, CanUpdateManagersPlan, CanSeeManagerSummary)
from partnership.resources import PartnerResource
from .models import Partnership, Deal, PartnershipLogs
from .serializers import (DealSerializer, PartnershipUpdateSerializer, DealCreateSerializer,
                          PartnershipTableSerializer, DealUpdateSerializer,
                          PartnershipCreateSerializer, PartnershipSerializer)


class PartnershipViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet,
                         PartnerExportViewSetMixin,
                         PartnerStatMixin):
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
                       filters.OrderingFilter,)
    filter_fields = ('user', 'responsible__user', 'responsible')
    ordering_fields = ('user__first_name', 'user__last_name', 'user__master__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__facebook',
                       'user__vkontakte', 'value', 'responsible__user__last_name')
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

    def perform_update(self, serializer):
        partner = serializer.save()
        PartnershipLogs.log_partner(partner)

    def perform_create(self, serializer):
        partner = serializer.save()
        PartnershipLogs.log_partner(partner)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permission() for permission in self.permission_list_classes]
        if self.action in ('update', 'partial_update'):
            return [permission() for permission in self.permission_update_classes]
        return super(PartnershipViewSet, self).get_permissions()

    @list_route(permission_classes=(IsAuthenticated, CanSeePartners))
    def simple(self, request):
        """
        Returns a list of partners with level >= ``manager`` (``manager``, ``supervisor``, ``director``).

        :param request: rest_framework.Request
        :return: list of dicts, e.g. [{'id': 124, 'fullname': Ivanov Ivan Ivanovich}, ...]
        """
        partnerships = Partnership.objects.select_related('user').filter(
            level__lte=Partnership.MANAGER).values_list(
            'id', 'user__last_name', 'user__first_name', 'user__middle_name')
        partnerships = [{'id': p[0], 'fullname': '{} {} {}'.format(*p[1:])} for p in partnerships]
        return Response(partnerships)

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

    @list_route(methods=['GET'], permission_classes=(CanSeeManagerSummary,))
    def managers_summary(self, request):
        year = int(request.query_params.get('year', datetime.now().year))
        month = int(request.query_params.get('month', datetime.now().month))

        partner_ids = self.queryset.filter(Q(level__lte=Partnership.MANAGER) | Q(
            disciples_deals__isnull=False)).distinct().prefetch_related('deals').values_list('id', flat=True)

        managers_query = Partnership.objects.filter(id__in=partner_ids).prefetch_related('deals')

        lookup_field = 'pk'
        logged_queryset = logged_managers_query = None

        if year != datetime.now().year or month != datetime.now().month:
            logged_year, logged_month = self.get_logged_period(year, month)
            logged_queryset, logged_managers_query = self.get_logged_queries(logged_year, logged_month)
            lookup_field = 'partner_id'

        managers = [{
            # Making queries from Partnership model
            'sum_pay': x[0] or 0,
            'sum_pay_tithe': x[1] or 0,
            'sum_deals': x[2] or 0,
            'manager': x[3],
            'partner_id': x[4],
            'user_id': x[5],
            # Making queries from PartnershipLogs model if requested period not in this month
            'total_partners': x[6] or 0,
            'active_partners': x[7] or 0,
            'potential_sum': x[8] or 0,
            'plan': x[9] or 0,

            } for x in zip(
            self._get_sum_pay(managers_query, year, month, deal_type=Deal.DONATION),
            self._get_sum_pay(managers_query, year, month, deal_type=Deal.TITHE),
            self._get_sum_deals(managers_query, year, month),
            self._get_partners(managers_query),
            self._get_partnerships_ids(managers_query),
            self._get_users_ids(managers_query),
            self._get_total_partners(logged_queryset or Partnership.objects.all(),
                                     logged_managers_query or managers_query,
                                     lookup_field),
            self._get_active_partners(logged_queryset or Partnership.objects.all(),
                                      logged_managers_query or managers_query,
                                      lookup_field),
            self._get_potential_sum(logged_queryset or Partnership.objects.all(),
                                    logged_managers_query or managers_query,
                                    lookup_field),
            self._get_managers_plan(logged_queryset or Partnership.objects.all(),
                                    logged_managers_query or managers_query,
                                    lookup_field),
        )]
        managers = self._order_managers(managers)
        managers = [manager for manager in managers if manager['potential_sum'] != 0 or
                    manager['sum_pay'] != 0 or manager['sum_pay_tithe'] != 0]

        return Response({'results': managers, 'table_columns': partnership_summary_table(self.request.user)})

    def _order_managers(self, managers):
        ordering = self.request.query_params.get('ordering', 'manager')
        ordering_fields = ['manager', 'sum_deals', 'total_partners', 'active_partners',
                           'potential_sum', 'sum_pay', 'manager_plan', 'sum_pay_tithe']

        if ordering.strip('-') in ordering_fields:
            managers.sort(key=lambda obj: obj[ordering.strip('-')], reverse=ordering.startswith('-'))
        return managers

    """
    Making queries from Partnership model
    """
    @staticmethod
    def _get_sum_pay(queryset, year, month, deal_type):
        raw = """
          select p.id,
          (select sum(pay.sum) from payment_payment pay WHERE pay.content_type_id = 40 and
          pay.object_id in (select d.id from partnership_deal d where d.responsible_id = p.id and d.type = {0} and
          (d.date_created BETWEEN '{1}-01-01' and '{1}-12-31') and
          extract('month' from d.date_created) = {2} )) sum
          from partnership_partnership p
          WHERE p.id in (
              SELECT pp.id from partnership_partnership pp
              LEFT OUTER JOIN partnership_deal d ON (pp.id = d.responsible_id)
              WHERE pp.level <= {3} OR d.id IS NOT NULL)
          ORDER BY p.id;
          """.format(deal_type, year, month, Partnership.MANAGER)

        return [p.sum for p in queryset.raw(raw)]

    @staticmethod
    def _get_sum_deals(queryset, year, month):
        subqs_deals = Deal.objects.filter(date_created__year=year, date_created__month=month, responsible=OuterRef(
            'pk')).order_by().values('responsible').annotate(deals_sum=Sum('value')).values('deals_sum')

        return Partnership.objects.filter(id__in=queryset).annotate(
            sum_deals=Subquery(subqs_deals, output_field=DecimalField())).values_list(
            'sum_deals', flat=True).order_by('id')

    @staticmethod
    def _get_partners(queryset):
        return queryset.annotate(managers=Concat(
            'user__last_name', V(' '), 'user__first_name', V(' '), 'user__middle_name')).values_list(
            'managers', flat=True).order_by('id')

    @staticmethod
    def _get_partnerships_ids(queryset):
        return Partnership.objects.filter(id__in=queryset).values_list('id', flat=True).order_by('id')

    @staticmethod
    def _get_users_ids(queryset):
        return Partnership.objects.filter(id__in=queryset).values_list('user__id', flat=True).order_by('id')

    """
    Making queries from PartnershipLogs model if requested period not in this month
    """
    @staticmethod
    def get_logged_queries(log_year, log_month):
        raw = """
              SELECT id FROM partnership_partnershiplogs WHERE id IN (
              SELECT (SELECT pl.id FROM partnership_partnershiplogs pl WHERE p.id = pl.partner_id AND
              pl.log_date < '%s-%s-01'
              ORDER BY log_date DESC LIMIT 1
              ) p_log_id
              FROM partnership_partnership p ORDER BY p.id);
              """ % (log_year, log_month)

        with connection.cursor() as connect:
            connect.execute(raw)
            result = connect.fetchall()

        logged_ids = [k[0] for k in result]  # from arrays with tuples of ids to array with integer ids

        logged_queryset = PartnershipLogs.objects.filter(id__in=logged_ids)

        logged_managers_query = logged_queryset.filter(Q(level__lte=PartnershipLogs.MANAGER) | Q(
            partner__disciples_deals__isnull=False)).distinct().prefetch_related('partner', 'responsible')

        return logged_queryset, logged_managers_query

    @staticmethod
    def get_logged_period(year, month):
        """
        Create year and month params for PartnershipLogs queries
        """
        if month == 12:
            month = 1
            year += 1
            return year, month

        return year, month + 1

    @staticmethod
    def _get_total_partners(queryset, managers, lookup_field):
        subqs_partners = queryset.filter(responsible=OuterRef(lookup_field)).order_by().values(
            'responsible').annotate(count=Count('id')).values('count')

        return queryset.filter(id__in=managers).annotate(total_partners=Subquery(
            subqs_partners, output_field=IntegerField())).values_list(
            'total_partners', flat=True).order_by(lookup_field)

    @staticmethod
    def _get_active_partners(queryset, managers, lookup_field):
        subqs_active_partners = queryset.filter(
            responsible=OuterRef(lookup_field), is_active=True).order_by().values('responsible').annotate(
            count=Count('id')).values('count')

        return queryset.filter(id__in=managers).annotate(active_partners=Subquery(
            subqs_active_partners, output_field=IntegerField())).values_list(
            'active_partners', flat=True).order_by(lookup_field)

    @staticmethod
    def _get_potential_sum(queryset, managers, lookup_field):
        subqs_potential_sum = queryset.filter(responsible=OuterRef(lookup_field)).order_by().values(
            'responsible').annotate(potential_sum=Sum('value')).values('potential_sum')

        return queryset.filter(id__in=managers).annotate(
            potential_sum=Subquery(subqs_potential_sum, output_field=DecimalField())).values_list(
            'potential_sum', flat=True).order_by(lookup_field)

    @staticmethod
    def _get_managers_plan(queryset, managers, lookup_field):
        return queryset.filter(id__in=managers).values_list('plan', flat=True).order_by(lookup_field)

    @detail_route(methods=['POST'], permission_classes=(CanUpdateManagersPlan,))
    def set_plan(self, request, pk):
        manager = get_object_or_404(Partnership, pk=pk)
        plan_sum = request.data.get('plan_sum')
        if not plan_sum:
            raise exceptions.ValidationError({'message': _('Parameter {plan_sum} not passed')})
        try:
            plan_sum = Decimal(plan_sum)
        except Exception as e:
            print(e)
            raise exceptions.ValidationError({'message': _('Parameter {plan_sum} must be Integer')})

        manager.plan = plan_sum
        manager.save()
        PartnershipLogs.log_partner(manager)

        return Response({'message': 'План менеджера успешно установлен в %s' % manager.plan})


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
                       'responsible__user__last_name',
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
