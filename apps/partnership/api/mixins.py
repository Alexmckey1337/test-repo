import logging
from collections import Counter
from datetime import datetime
from time import time

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import connection
from django.db.models import (
    Sum, When, Case, F, IntegerField, Q, DecimalField, OuterRef, Subquery, Value as V)
from django.db.models.functions import Coalesce, Concat
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from apps.account.models import CustomUser
from common.views_mixins import ExportViewSetMixin
from apps.partnership.models import Partnership, Deal, PartnershipLogs
from apps.payment.api.views_mixins import CreatePaymentMixin, ListPaymentMixin
from apps.partnership.api.permissions import (
    CanSeePartnerStatistics, CanCreatePartnerPayment, CanSeeDealPayments,
    CanExportPartnerList, CanSeeManagerSummary, CanCreateChurchPartnerPayment, CanSeeChurchDealPayments,
    CanExportChurchPartnerList)
from apps.payment.models import Payment, Currency
from apps.navigation.table_columns import get_table

sql_logger = logging.Logger('partner.sql')


def func_time(func):
    def wrap(*args, **kwargs):
        t = time()
        result = func(*args, **kwargs)
        sql_logger.warning("[{1:.3f}] {0}".format(func.__name__, time() - t))
        return result

    return wrap


class PartnerStatMixin:
    @list_route(methods=['get'], permission_classes=(IsAuthenticated, CanSeePartnerStatistics))
    def stats_payments(self, request):
        current_manager = request.user

        self.check_stats_permissions(current_manager)

        deals = self.get_deals_of_partner(request, current_manager)
        deals = self.filter_deals_by_month(request, deals)
        # deals = Deal.objects.all()  # for test, del this
        stats = dict()

        deals_with_sum = deals.annotate(total_sum=Coalesce(Sum('payments__sum'), V(0)))

        stats['deals'] = self.stats_by_deals(deals, deals_with_sum)
        stats['partners'] = self.stats_by_partners(deals, deals_with_sum)
        # stats['sum'] = self.stats_by_sum(deals, deals_with_sum)

        return Response(stats)

    @list_route(methods=['get'], renderer_classes=(TemplateHTMLRenderer,),
                permission_classes=(IsAuthenticated, CanSeePartnerStatistics))
    def stat_deals(self, request):
        current_manager = request.user

        self.check_stats_permissions(current_manager)

        deals = self.get_deals_of_partner(request, current_manager)
        deals = self.filter_deals_by_month(request, deals)
        deals = deals.base_queryset(). \
            annotate_full_name(). \
            annotate_responsible_name(). \
            annotate_total_sum(). \
            order_by('-date_created', 'id')
        #
        # serializer = DealSerializer(deals, many=True)

        return Response({'deals': deals}, template_name='partner/partials/stat_deals.html')

    @list_route(methods=['get'], renderer_classes=(TemplateHTMLRenderer,),
                permission_classes=(IsAuthenticated, CanSeePartnerStatistics))
    def stat_payments(self, request):
        current_manager = request.user

        self.check_stats_permissions(current_manager)

        deals = self.get_deals_of_partner(request, current_manager)
        deals = self.filter_deals_by_month(request, deals)
        deals_ids = set(deals.values_list('id', flat=True))
        content_type = ContentType.objects.get_for_model(Deal)
        payments = Payment.objects.filter(
            content_type=content_type, object_id__in=deals_ids)
        #
        # serializer = PaymentShowSerializer(payments, many=True)

        return Response({'payments': payments}, template_name='partner/partials/stat_payments.html')

    # Helpers

    @staticmethod
    def check_stats_permissions(current_manager):
        if not current_manager.is_partner_manager_or_high:
            raise PermissionDenied({'detail': _('Статистику можно просматривать только менеджерам.')})

    @staticmethod
    def get_deals_of_partner(request, current_manager):
        request_manager_id = request.query_params.get('partner_id')

        if current_manager.is_partner_manager or not request_manager_id:
            return current_manager.disciples_deals
        if request_manager_id == 'all':
            return Deal.objects.filter(responsible__isnull=False)
        manager = get_object_or_404(CustomUser, id=request_manager_id)
        return manager.disciples_deals

    @staticmethod
    def filter_deals_by_month(request, deals):
        month = request.query_params.get('month', timezone.now().month)
        year = request.query_params.get('year', timezone.now().year)

        return deals.filter(date_created__month=month, date_created__year=year)

    @staticmethod
    def stats_by_deals(deals, deals_with_sum):
        paid = deals_with_sum.filter(total_sum__gte=F('value')).count()
        unpaid = deals_with_sum.filter(total_sum__lt=F('value'), total_sum=0).count()
        partial_paid = deals_with_sum.filter(total_sum__lt=F('value'), total_sum__gt=0).count()
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
            total_sum=0).aggregate(p=ArrayAgg('partnership'))['p'])
        partial_paid = set(deals_with_sum.filter(
            total_sum__lt=F('value'),
            total_sum__gt=0).aggregate(p=ArrayAgg('partnership'))['p'])
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
                sum_planed=Coalesce(Sum('value'), V(0)),
                sum_paid=Coalesce(Sum('total_sum'), V(0)))
            closed_paid_sum = deals_with_sum.filter(currency=c, done=True).aggregate(
                sum_planed=Coalesce(Sum('value'), V(0)),
                sum_paid=Coalesce(Sum('total_sum'), V(0)))
            sum[c.code] = {
                'currency_name': c.name,
                'total_paid_sum': total_paid_sum,
                'closed_paid_sum': closed_paid_sum
            }
        return sum


class ManagerSummaryMixin:
    @list_route(methods=['GET'], permission_classes=(CanSeeManagerSummary,))
    def managers_summary(self, request):
        year = int(request.query_params.get('year', datetime.now().year))
        month = int(request.query_params.get('month', datetime.now().month))

        managers_query, partners, plan = self._get_start_data()

        partners_data = self._get_partners(managers_query)
        managers = [{
            # Making queries from Partnership model
            'sum_pay': x[0] or 0,
            'sum_pay_tithe': x[1] or 0,
            'sum_deals': x[2] or 0,
            'manager': x[3],
            'user_id': x[4],
            # Making queries from PartnershipLoUntitled Diagram.xmlgs model if requested period not in this month
            'total_partners': x[5] or 0,
            'active_partners': x[6] or 0,
            'potential_sum': x[7] or 0,
            'plan': x[8] or 0,

        } for x in zip(
            self._get_sum_pay(year, month, deal_type=Deal.DONATION),
            self._get_sum_pay(year, month, deal_type=Deal.TITHE),
            self._get_sum_deals(managers_query, year, month),
            [p['full_name'] for p in partners_data],
            [p['id'] for p in partners_data],
            self._get_total_partners(partners, managers_query),
            self._get_active_partners(partners, managers_query),
            self._get_potential_sum(partners, managers_query),
            plan,
        )]
        managers = [manager for manager in managers if (
                manager['potential_sum'] != 0 or
                manager['sum_pay'] != 0 or
                manager['sum_pay_tithe'] != 0)]
        managers = self._order_managers(managers)

        return Response({'results': managers, 'table_columns': get_table('partner_summary', self.request.user.id)})

    def _get_start_data(self):
        year = int(self.request.query_params.get('year', datetime.now().year))
        month = int(self.request.query_params.get('month', datetime.now().month))

        manager_ids = CustomUser.objects.filter(Q(partner_role__isnull=False) | Q(
            disciples_deals__isnull=False)).distinct().values_list('id', flat=True)

        managers = CustomUser.objects.filter(id__in=manager_ids).order_by('pk')

        plan = self._get_managers_plan(managers)
        partners = Partnership.objects.all()

        if year != datetime.now().year or month != datetime.now().month:
            logged_year, logged_month = self.get_logged_period(year, month)
            partners = self.get_logged_queries(logged_year, logged_month)
            managers, plan = self.get_logged_managers(logged_year, logged_month)
        return managers, partners, plan

    def _order_managers(self, managers):
        ordering = self.request.query_params.get('ordering', 'manager')
        ordering_fields = ['manager', 'sum_deals', 'total_partners', 'active_partners',
                           'potential_sum', 'sum_pay', 'manager_plan', 'sum_pay_tithe']

        if ordering.strip('-') in ordering_fields:
            managers.sort(key=lambda obj: obj[ordering.strip('-')], reverse=ordering.startswith('-'))
        return managers

    @staticmethod
    def _get_partners(queryset):
        return queryset.annotate(full_name=Concat(
            'last_name', V(' '), 'first_name', V(' '), 'middle_name')).values(
            'full_name', 'id').order_by('pk')

    """
    Making queries from Partnership model
    """

    def _get_sum_pay(self, year, month, deal_type):
        raw = """
          select u.user_ptr_id,
          (select sum(pay.sum) from payment_payment pay WHERE pay.content_type_id = 40 and
          pay.object_id in (select d.id from partnership_deal d where d.responsible_id = u.user_ptr_id and
          d.type = {0} and (d.date_created BETWEEN '{1}-01-01' and '{1}-12-31') and
          extract('month' from d.date_created) = {2} )) sum
          from account_customuser u
          WHERE u.user_ptr_id in (
              SELECT uu.user_ptr_id from account_customuser uu
              LEFT OUTER JOIN partnership_deal d ON (uu.user_ptr_id = d.responsible_id)
              LEFT OUTER JOIN partnership_partnerrolelog pr ON (uu.user_ptr_id = pr.user_id and pr.id IN (
                SELECT DISTINCT ON (user_id) (
                  SELECT pl.id
                  FROM partnership_partnerrolelog pl
                  WHERE p.user_id = pl.user_id and pl.log_date < '{4}-{5}-01'
                  ORDER BY pl.log_date DESC LIMIT 1
                ) FROM partnership_partnerrolelog p) and pr.deleted = false)
              WHERE pr.id IS NOT NULL OR d.id IS NOT NULL)
          ORDER BY u.user_ptr_id;
          """.format(deal_type, year, month, settings.PARTNER_LEVELS['manager'], *self.get_logged_period(year, month))

        with connection.cursor() as connect:
            connect.execute(raw)
            result = connect.fetchall()

        for k in result:
            yield k[1]

    @staticmethod
    def _get_sum_deals(queryset, year, month):
        subqs_deals = Deal.objects.filter(date_created__year=year, date_created__month=month, responsible=OuterRef(
            'pk')).order_by().values('responsible').annotate(deals_sum=Sum('value')).values('deals_sum')

        return queryset.annotate(
            sum_deals=Subquery(subqs_deals, output_field=DecimalField())).values_list(
            'sum_deals', flat=True)

    """
    Making queries from PartnershipLogs model if requested period not in this month
    """

    @staticmethod
    @func_time
    def get_logged_queries(log_year, log_month):
        raw = """
              SELECT (SELECT pl.id FROM partnership_partnershiplogs pl WHERE p.id = pl.partner_id AND
              pl.log_date < '%s-%s-01'
              ORDER BY log_date DESC LIMIT 1
              ) p_log_id
              FROM partnership_partnership p ORDER BY p.id;
              """ % (log_year, log_month)

        with connection.cursor() as connect:
            connect.execute(raw)
            result = connect.fetchall()

        logged_ids = [k[0] for k in result]  # from arrays with tuples of ids to array with integer ids

        logged_queryset = PartnershipLogs.objects.filter(id__in=logged_ids)

        return logged_queryset

    @staticmethod
    @func_time
    def get_logged_managers(log_year, log_month):
        raw = """
                SELECT log.user_id, log.plan FROM partnership_partnerrolelog log WHERE id IN (
                SELECT DISTINCT ON (user_id) (
                  SELECT pl.id
                  FROM partnership_partnerrolelog pl
                  WHERE p.user_id = pl.user_id and pl.log_date < '%s-%s-01'
                  ORDER BY pl.log_date DESC LIMIT 1
                ) FROM partnership_partnerrolelog p) and log.deleted = false ORDER BY log.user_id;
              """ % (log_year, log_month)

        with connection.cursor() as connect:
            connect.execute(raw)
            result = connect.fetchall()

        managers_query = list(set(CustomUser.objects.filter(
            Q(id__in=[k[0] for k in result]) |
            Q(disciples_deals__isnull=False)
        ).order_by().only('pk').distinct('pk').values_list('id', flat=True)))
        plan = []
        for m in sorted(managers_query):
            p = 0
            for r in result:
                if r[0] == m:
                    p = r[1]
                    break
            plan.append(p)
        managers_query = CustomUser.objects.filter(id__in=managers_query).order_by('pk')

        return managers_query, plan

    @staticmethod
    def get_logged_period(year, month):
        """
        Create year and month params for PartnershipLogs queries
        """
        if month == 12:
            return year + 1, 1

        return year, month + 1

    @staticmethod
    def _get_total_partners(queryset, managers):
        s = dict(Counter(list(queryset.order_by().values_list('responsible', flat=True))))
        for m in managers:
            yield s.get(m.pk, 0)

    @staticmethod
    def _get_active_partners(queryset, managers):
        s = dict(Counter(list(queryset.filter(is_active=True).order_by().values_list('responsible', flat=True))))
        for m in managers:
            yield s.get(m.pk, 0)

    @staticmethod
    def _get_potential_sum(queryset, managers):
        s = list(queryset.order_by().values('responsible', 'value'))
        for m in managers:
            yield sum([f['value'] for f in filter(lambda z: z['responsible'] == m.pk, s)])

    @staticmethod
    def _get_managers_plan(managers):
        return managers.values_list('partner_role__plan', flat=True).order_by('pk')


class DealCreatePaymentMixin(CreatePaymentMixin):
    @detail_route(methods=['post'], permission_classes=(IsAuthenticated, CanCreatePartnerPayment))
    def create_payment(self, request, pk=None):
        return self._create_payment(request, pk)


class DealListPaymentMixin(ListPaymentMixin):
    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, CanSeeDealPayments))
    def payments(self, request, pk=None):
        return self._payments(request, pk)


class ChurchDealCreatePaymentMixin(CreatePaymentMixin):
    @detail_route(methods=['post'], permission_classes=(IsAuthenticated, CanCreateChurchPartnerPayment))
    def create_payment(self, request, pk=None):
        return self._create_payment(request, pk)


class ChurchDealListPaymentMixin(ListPaymentMixin):
    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, CanSeeChurchDealPayments))
    def payments(self, request, pk=None):
        return self._payments(request, pk)


class PartnerExportViewSetMixin(ExportViewSetMixin):
    @list_route(methods=['post'], permission_classes=(IsAuthenticated, CanExportPartnerList,))
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


class ChurchPartnerExportViewSetMixin(ExportViewSetMixin):
    @list_route(methods=['post'], permission_classes=(IsAuthenticated, CanExportChurchPartnerList,))
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


class PartnerStatusReviewMixin(object):
    @staticmethod
    def partnership_status_review(partner):
        value = False
        for deal in partner.deals.order_by('-date_created')[:3]:
            if not (deal.expired and not deal.done):
                value = True

        if value and not partner.is_active:
            partner.is_active = True
            partner.save()

        if not value and partner.is_active:
            partner.is_active = False
            partner.save()
