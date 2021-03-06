import logging
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import connection
from django.db.models import (
    Sum, When, Case, F, IntegerField, Q, DecimalField, OuterRef, Subquery, Value as V)
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from apps.account.models import CustomUser
from apps.navigation.table_columns import get_table
from apps.partnership.api.permissions import (
    CanSeePartnerStatistics, CanCreatePartnerPayment, CanSeeDealPayments,
    CanExportPartnerList, CanSeeManagerSummary, CanCreateChurchPartnerPayment, CanSeeChurchDealPayments,
    CanExportChurchPartnerList)
from apps.partnership.api.reports import (
    get_next_month, _get_managers_plan, get_logged_managers, get_logged_partners, get_managers_stats_cached)
from apps.partnership.models import Partnership, Deal
from apps.payment.api.views_mixins import CreatePaymentMixin, ListPaymentMixin
from apps.payment.models import Payment, Currency
from common.performance import func_time
from common.views_mixins import ExportViewSetMixin

sql_logger = logging.Logger('partner.sql')


class PartnerStatMixin:
    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated, CanSeePartnerStatistics))
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

    @action(detail=False, methods=['get'], renderer_classes=(TemplateHTMLRenderer,),
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

    @action(detail=False, methods=['get'], renderer_classes=(TemplateHTMLRenderer,),
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


class StatsByManagersMixin:
    @action(detail=False, methods=['GET'], permission_classes=(CanSeeManagerSummary,))
    def managers_summary(self, request):
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))

        managers, last_update = get_managers_stats_cached(year, month)
        managers = self._order_managers(managers)

        return Response({
            'results': managers,
            'last_update': last_update,
            'table_columns': get_table('partner_summary', self.request.user.id),
        })

    @func_time
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

    """
    Making queries from PartnershipLogs model if requested period not in this month
    """


class StatsByMonthsMixin:
    @action(detail=False, methods=['GET'], permission_classes=(CanSeeManagerSummary,), url_path='all/manager_summary')
    def managers_by_period(self, request):
        return Response(data=self._get_manager_summary(request.query_params.get('period', '3month')))

    @action(detail=True, methods=['GET'], permission_classes=(CanSeeManagerSummary,))
    def manager_summary(self, request, pk=None):
        user = get_object_or_404(CustomUser, pk=pk)
        return Response(data=self._get_manager_summary(request.query_params.get('period', '3month'), user))

    @staticmethod
    def _get_month_period(period):
        now = timezone.now()
        month_end = now.year * 12 + now.month - 1
        if period == '3month':
            month_start = month_end - 3
        elif period == '6month':
            month_start = month_end - 6
        elif period == 'year':
            month_start = month_end - 12
        elif period == '30month':
            month_start = month_end - 30
        else:
            month_start = month_end - 3
        return month_start, month_end

    def _get_manager_summary(self, period, user=None):
        month_start, month_end = self._get_month_period(period)

        deals = self._get_deal_sum_by_months(month_start, manager=user)
        church_deals = self._get_church_deal_sum_by_months(month_start, manager=user)
        payments = self._get_payment_sum_by_months(month_start, manager=user)
        payments_t1 = self._get_payment_sum_by_months(month_start, type=1, manager=user)
        payments_t2 = self._get_payment_sum_by_months(month_start, type=2, manager=user)
        payments_t3 = self._get_church_payment_sum_by_months(month_start, manager=user)
        plans = self._get_plans_by_months(month_start, month_end, manager=user)
        partners = self._get_partners_by_months(month_start, month_end, manager=user)
        church_partners = self._get_church_partners_by_months(month_start, month_end, manager=user)

        tt = {}
        for i in range(month_end, month_start, -1):
            k = '{}-{:02d}'.format(i // 12, i % 12 + 1)
            tt[k] = {
                'payments': payments.get(k, 0),
                'payments_t1': payments_t1.get(k, 0),
                'payments_t2': payments_t2.get(k, 0),
                'payments_t3': payments_t3.get(k, 0),
                'deals': deals.get(k, 0),
                'church_deals': church_deals.get(k, 0),
                'plans': plans.get(k, 0),
                'partners_count': len(partners[k]),
                'active_partners_count': len(tuple(filter(lambda p: bool(p[1]), partners[k]))),
                'church_partners_count': len(church_partners[k]),
                'church_active_partners_count': len(tuple(filter(lambda p: bool(p[1]), church_partners[k]))),
                'potential': sum([p[0] for p in partners[k]]),
                'church_potential': sum([p[0] for p in church_partners[k]]),
            }
        return tt

    @staticmethod
    @func_time
    def _get_plans_by_months(_from, to, manager=None):
        if manager:
            months = ', '.join(["('{}-{:02d}')".format(i // 12, i % 12 + 1) for i in range(to, _from, -1)])
            raw = """
                SELECT
                  p.month,
                  coalesce(
                      (SELECT pl.plan
                       FROM partnership_partnerrolelog pl
                       WHERE pl.log_date < to_date(p.month, 'YYYY-MM') + interval '1 month' AND pl.user_id = {manager}
                       ORDER BY pl.log_date DESC
                       LIMIT 1),
                      0) plan
                FROM (VALUES {months}) AS p(month);
                """.format(manager=manager.id, months=months)

            with connection.cursor() as connect:
                connect.execute(raw)
                result = connect.fetchall()
        else:
            result = list()
            months = ["{}-{:02d}".format(i // 12, i % 12 + 1) for i in range(to, _from, -1)]
            for month in months:
                raw = """
                    SELECT
                      coalesce(sum(log.plan), 0)
                    FROM partnership_partnerrolelog log
                    WHERE id IN (
                      SELECT DISTINCT ON (user_id) (
                        SELECT pl.id
                        FROM partnership_partnerrolelog pl
                        WHERE p.user_id = pl.user_id AND
                        pl.log_date < to_date('{month}', 'YYYY-MM-DD') + INTERVAL '1 month'
                        ORDER BY pl.log_date DESC
                        LIMIT 1
                      )
                    FROM partnership_partnerrolelog p) AND log.deleted = FALSE
                """.format(month=month)
                with connection.cursor() as connect:
                    connect.execute(raw)
                    r = connect.fetchone()
                result.append((month, r[0]))
        return {date: sum for date, sum in result}

    @staticmethod
    @func_time
    def _get_partners_by_months(_from, to, manager=None):
        partners = dict()
        months = ["{}-{:02d}".format(i // 12, i % 12 + 1) for i in range(to, _from, -1)]
        manager = 'AND p.responsible_id = {}'.format(manager.id) if manager else ''
        for month in months:
            raw = """
                SELECT pp.value, pp.is_active
                FROM partnership_partnershiplogs pp
                WHERE pp.id IN (
                  SELECT (SELECT pl.id
                          FROM partnership_partnershiplogs pl
                          WHERE p.id = pl.partner_id AND
                                pl.log_date < to_date('{month}', 'YYYY-MM') + interval '1 month' {manager}
                          ORDER BY log_date DESC
                          LIMIT 1
                         ) p_log_id
                  FROM partnership_partnership p
                  ORDER BY p.id);
                """.format(manager=manager, month=month)

            with connection.cursor() as connect:
                connect.execute(raw)
                result = connect.fetchall()
            partners[month] = result
        return partners

    @staticmethod
    @func_time
    def _get_church_partners_by_months(_from, to, manager=None):
        partners = dict()
        months = ["{}-{:02d}".format(i // 12, i % 12 + 1) for i in range(to, _from, -1)]
        manager = 'AND p.responsible_id = {}'.format(manager.id) if manager else ''
        for month in months:
            raw = """
                SELECT pp.value, pp.is_active
                FROM partnership_churchpartnerlog pp
                WHERE pp.id IN (
                  SELECT (SELECT pl.id
                          FROM partnership_churchpartnerlog pl
                          WHERE p.id = pl.partner_id AND
                                pl.log_date < to_date('{month}', 'YYYY-MM') + interval '1 month' {manager}
                          ORDER BY log_date DESC
                          LIMIT 1
                         ) p_log_id
                  FROM partnership_churchpartner p
                  ORDER BY p.id);
                """.format(manager=manager, month=month)

            with connection.cursor() as connect:
                connect.execute(raw)
                result = connect.fetchall()
            partners[month] = result
        return partners

    @staticmethod
    @func_time
    def _get_deal_sum_by_months(month, manager=None):
        if month % 12:
            month = '{}-{}'.format(month // 12, month % 12)
        else:
            month = '{}-{}'.format(month // 12 - 1, 12)
        manager = 'AND d.responsible_id = {}'.format(manager.id) if manager else ''
        raw = """
            SELECT
              to_char(d.date_created, 'YYYY-MM'),
              sum(d.value)
            FROM partnership_deal d
            WHERE d.date_created >= '{month}-01' {manager}
            GROUP BY to_char(d.date_created, 'YYYY-MM')
            ORDER BY to_char(d.date_created, 'YYYY-MM') DESC;
            """.format(manager=manager, month=month)

        with connection.cursor() as connect:
            connect.execute(raw)
            result = connect.fetchall()
        return {date: sum for date, sum in result}

    @staticmethod
    @func_time
    def _get_church_deal_sum_by_months(month, manager=None):
        if month % 12:
            month = '{}-{}'.format(month // 12, month % 12)
        else:
            month = '{}-{}'.format(month // 12 - 1, 12)
        manager = 'AND d.responsible_id = {}'.format(manager.id) if manager else ''
        raw = """
            SELECT
              to_char(d.date_created, 'YYYY-MM'),
              sum(d.value)
            FROM partnership_churchdeal d
            WHERE d.date_created >= '{month}-01' {manager}
            GROUP BY to_char(d.date_created, 'YYYY-MM')
            ORDER BY to_char(d.date_created, 'YYYY-MM') DESC;
            """.format(manager=manager, month=month)

        with connection.cursor() as connect:
            connect.execute(raw)
            result = connect.fetchall()
        return {date: sum for date, sum in result}

    @staticmethod
    @func_time
    def _get_payment_sum_by_months(month, type=None, manager=None):
        if month % 12:
            month = '{}-{}'.format(month // 12, month % 12)
        else:
            month = '{}-{}'.format(month // 12 - 1, 12)
        manager = 'AND d.responsible_id = {}'.format(manager.id) if manager else ''
        raw = """
            SELECT
              to_char(d.date_created, 'YYYY-MM'),
              sum(p.sum)
            FROM payment_payment p
              JOIN partnership_deal d ON p.object_id = d.id AND p.content_type_id = 40
            WHERE d.date_created >= '{month}-01' {type} {manager}
            GROUP BY to_char(d.date_created, 'YYYY-MM')
            ORDER BY to_char(d.date_created, 'YYYY-MM') DESC;
            """.format(
            manager=manager,
            month=month,
            type='AND d.type = %s' % type if type else '')

        with connection.cursor() as connect:
            connect.execute(raw)
            result = connect.fetchall()
        return {date: sum for date, sum in result}

    def _get_start_data(self):
        year = int(self.request.query_params.get('year', timezone.now().year))
        month = int(self.request.query_params.get('month', timezone.now().month))

        manager_ids = CustomUser.objects.filter(Q(partner_role__isnull=False) | Q(
            disciples_deals__isnull=False)).distinct().values_list('id', flat=True)

        managers = CustomUser.objects.filter(id__in=manager_ids).order_by('pk')

        plan = _get_managers_plan(managers)
        partners = Partnership.objects.all()

        if year != timezone.now().year or month != datetime.now().month:
            next_month = get_next_month(year, month)
            partners = get_logged_partners(next_month)
            managers, plan = get_logged_managers(next_month)
        return managers, partners, plan

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

    def _get_sum_pay(self, year, month, deal_type):
        raw = """
          select u.user_ptr_id,
          (select sum(pay.sum) from payment_payment pay WHERE pay.content_type_id = 40 and
          pay.object_id in (select d.id from partnership_deal d where d.responsible_id = u.user_ptr_id and
          d.type = {type} and d.date_created = '{year}-{month:02d}')) sum
          from account_customuser u
          WHERE u.user_ptr_id in (
              SELECT uu.user_ptr_id from account_customuser uu
              LEFT OUTER JOIN partnership_deal d ON (uu.user_ptr_id = d.responsible_id)
              LEFT OUTER JOIN partnership_partnerrolelog pr ON (uu.user_ptr_id = pr.user_id and pr.id IN (
                SELECT DISTINCT ON (user_id) (
                  SELECT pl.id
                  FROM partnership_partnerrolelog pl
                  WHERE p.user_id = pl.user_id and pl.log_date < '{next_month}-01'
                  ORDER BY pl.log_date DESC LIMIT 1
                ) FROM partnership_partnerrolelog p) and pr.deleted = false)
              WHERE pr.id IS NOT NULL OR d.id IS NOT NULL)
          ORDER BY u.user_ptr_id;
          """.format(type=deal_type, year=year, month=month, next_month=get_next_month(year, month))

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
    def _get_church_payment_sum_by_months(month, manager=None):
        if month % 12:
            month = '{}-{}'.format(month // 12, month % 12)
        else:
            month = '{}-{}'.format(month // 12 - 1, 12)
        manager = 'AND d.responsible_id = {}'.format(manager.id) if manager else ''
        raw = """
            SELECT
              to_char(d.date_created, 'YYYY-MM'),
              sum(p.sum)
            FROM payment_payment p
              JOIN partnership_churchdeal d ON p.object_id = d.id AND p.content_type_id = 103
            WHERE d.date_created >= '{month}-01' {manager}
            GROUP BY to_char(d.date_created, 'YYYY-MM')
            ORDER BY to_char(d.date_created, 'YYYY-MM') DESC;
            """.format(
            manager=manager,
            month=month)

        with connection.cursor() as connect:
            connect.execute(raw)
            result = connect.fetchall()
        return {date: sum for date, sum in result}


class StatsSummaryMixin(StatsByManagersMixin, StatsByMonthsMixin):
    pass


class DealCreatePaymentMixin(CreatePaymentMixin):
    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated, CanCreatePartnerPayment))
    def create_payment(self, request, pk=None):
        return self._create_payment(request, pk)


class DealListPaymentMixin(ListPaymentMixin):
    @action(detail=True, methods=['get'], permission_classes=(IsAuthenticated, CanSeeDealPayments))
    def payments(self, request, pk=None):
        return self._payments(request, pk)


class ChurchDealCreatePaymentMixin(CreatePaymentMixin):
    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated, CanCreateChurchPartnerPayment))
    def create_payment(self, request, pk=None):
        return self._create_payment(request, pk)


class ChurchDealListPaymentMixin(ListPaymentMixin):
    @action(detail=True, methods=['get'], permission_classes=(IsAuthenticated, CanSeeChurchDealPayments))
    def payments(self, request, pk=None):
        return self._payments(request, pk)


class PartnerExportViewSetMixin(ExportViewSetMixin):
    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated, CanExportPartnerList,))
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)

    def get_export_fields(self, data):
        fields = self.str_to_list_by_comma(data.get('fields', '')) or None
        for f in fields:
            f0, *lst = f.split('.')
            yield lst[0] if lst else f0


class ChurchPartnerExportViewSetMixin(ExportViewSetMixin):
    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated, CanExportChurchPartnerList,))
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


class PartnerStatusReviewMixin(object):
    @staticmethod
    def partnership_status_review(partner):
        value = False
        for deal in partner.deals.order_by('-date_created', 'pk')[:3]:
            if not (deal.expired and not deal.done):
                value = True

        if value and not partner.is_active:
            partner.is_active = True
            partner.save()

        if not value and partner.is_active:
            partner.is_active = False
            partner.save()
