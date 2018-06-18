import json
import logging
from collections.__init__ import Counter
from datetime import datetime
from typing import Tuple, List

from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.db.models import QuerySet, OuterRef, Sum, Subquery, DecimalField, Q, Value as V
from django.db.models.functions import Concat
from django.utils import timezone

from apps.account.models import CustomUser
from apps.notification.backend import RedisBackend
# from common.performance import func_time
from apps.partnership.models import Deal, ChurchDeal, PartnershipLogs, ChurchPartnerLog, Partnership, ChurchPartner
from apps.partnership.tasks import managers_summary
from common.utils import encode_month, decode_month

logger = logging.Logger('partner.sql')


class ManagersSummaryCacheError(Exception):
    pass


class ManagersSummaryCache:
    key_template = 'partner:managers_summary:{}'

    def __init__(self):
        self.redis = RedisBackend()

    def get(self, month_code: int) -> Tuple[str, List]:
        s = self.redis.get(self.key_template.format(month_code))
        if not s:
            year, month = decode_month(month_code)
            raise ManagersSummaryCacheError(f'Cache for month = {year}-{month:02d} not exist')
        data = json.loads(s)
        return data['data'], data['last_update']

    def set(self, month_code: int, data: List):
        data = {"data": data, "last_update": timezone.now()}
        data = json.dumps(data, cls=DjangoJSONEncoder)
        self.redis.set(self.key_template.format(month_code), data)


def get_next_month(year: int, month: int) -> str:
    """
    Create year and month params for PartnershipLogs queries
    """
    if month == 12:
        return '{year}-{month}'.format(year=year + 1, month=1)
    return '{year}-{month}'.format(year=year, month=month + 1)


# @func_time
def _get_sum_pay(year: int, month: int, deal_type: int) -> list:
    raw = """
      select u.user_ptr_id,
      (select sum(pay.sum) from payment_payment pay WHERE pay.content_type_id = 40 and
      pay.object_id in (select d.id from partnership_deal d where d.responsible_id = u.user_ptr_id and
      d.type = {type} and to_char(d.date_created, 'YYYY-MM') = '{year}-{month:02d}')) sum
      from account_customuser u
      WHERE u.user_ptr_id in (
          SELECT uu.user_ptr_id from account_customuser uu
          LEFT OUTER JOIN partnership_deal d ON (uu.user_ptr_id = d.responsible_id)
          LEFT OUTER JOIN partnership_churchdeal cd ON (uu.user_ptr_id = cd.responsible_id)
          LEFT OUTER JOIN partnership_partnerrolelog pr ON (uu.user_ptr_id = pr.user_id and pr.id IN (
            SELECT DISTINCT ON (user_id) (
              SELECT pl.id
              FROM partnership_partnerrolelog pl
              WHERE p.user_id = pl.user_id and pl.log_date < '{next_month}-01'
              ORDER BY pl.log_date DESC LIMIT 1
            ) FROM partnership_partnerrolelog p) and pr.deleted = false)
          WHERE pr.id IS NOT NULL OR d.id IS NOT NULL OR cd.id IS NOT NULL)
      ORDER BY u.user_ptr_id;
      """.format(type=deal_type, year=year, month=month, next_month=get_next_month(year, month))

    with connection.cursor() as connect:
        connect.execute(raw)
        result = connect.fetchall()

    return [k[1] for k in result]


# @func_time
def _get_sum_church_pay(year: int, month: int) -> list:
    raw = """
      select u.user_ptr_id,
      (select sum(pay.sum) from payment_payment pay WHERE pay.content_type_id = 103 and
      pay.object_id in (select d.id from partnership_churchdeal d where d.responsible_id = u.user_ptr_id and
      to_char(d.date_created, 'YYYY-MM') = '{year}-{month:02d}')) sum
      from account_customuser u
      WHERE u.user_ptr_id in (
          SELECT uu.user_ptr_id from account_customuser uu
          LEFT OUTER JOIN partnership_deal d ON (uu.user_ptr_id = d.responsible_id)
          LEFT OUTER JOIN partnership_churchdeal cd ON (uu.user_ptr_id = cd.responsible_id)
          LEFT OUTER JOIN partnership_partnerrolelog pr ON (uu.user_ptr_id = pr.user_id and pr.id IN (
            SELECT DISTINCT ON (user_id) (
              SELECT pl.id
              FROM partnership_partnerrolelog pl
              WHERE p.user_id = pl.user_id and pl.log_date < '{next_month}-01'
              ORDER BY pl.log_date DESC LIMIT 1
            ) FROM partnership_partnerrolelog p) and pr.deleted = false)
          WHERE pr.id IS NOT NULL OR d.id IS NOT NULL OR cd.id IS NOT NULL)
      ORDER BY u.user_ptr_id;
      """.format(year=year, month=month, next_month=get_next_month(year, month))

    with connection.cursor() as connect:
        connect.execute(raw)
        result = connect.fetchall()

    return [k[1] for k in result]


# @func_time
def _get_sum_deals(queryset: QuerySet, year: int, month: int) -> list:
    subqs_deals = Deal.objects.filter(date_created__year=year, date_created__month=month, responsible=OuterRef(
        'pk')).order_by().values('responsible').annotate(deals_sum=Sum('value')).values('deals_sum')

    return list(queryset.annotate(
        sum_deals=Subquery(subqs_deals, output_field=DecimalField())).values_list(
        'sum_deals', flat=True))


# @func_time
def _get_sum_church_deals(queryset: QuerySet, year: int, month: int) -> list:
    subqs_deals = ChurchDeal.objects.filter(
        date_created__year=year, date_created__month=month, responsible=OuterRef('pk')
    ).order_by().values('responsible').annotate(deals_sum=Sum('value')).values('deals_sum')

    return list(queryset.annotate(
        sum_deals=Subquery(subqs_deals, output_field=DecimalField())).values_list(
        'sum_deals', flat=True))


# @func_time
def _get_managers_plan(managers: QuerySet) -> list:
    return list(managers.values_list('partner_role__plan', flat=True).order_by('pk'))


# @func_time
def get_logged_managers(next_month: str) -> (QuerySet, list, list):
    raw = """
            SELECT log.user_id, log.plan FROM partnership_partnerrolelog log WHERE id IN (
            SELECT DISTINCT ON (user_id) (
              SELECT pl.id
              FROM partnership_partnerrolelog pl
              WHERE p.user_id = pl.user_id and pl.log_date < '%s-01'
              ORDER BY pl.log_date DESC LIMIT 1
            ) FROM partnership_partnerrolelog p) and log.deleted = false ORDER BY log.user_id;
          """ % next_month

    with connection.cursor() as connect:
        connect.execute(raw)
        result = connect.fetchall()

    managers_ids = list(set(CustomUser.objects.filter(
        Q(id__in=[k[0] for k in result]) |
        Q(disciples_deals__isnull=False) |
        Q(partner_disciples_deals__isnull=False)
    ).order_by().only('pk').values_list('id', flat=True)))
    plan = []
    managers_ids = sorted(managers_ids)
    for m in managers_ids:
        p = 0
        for r in result:
            if r[0] == m:
                p = r[1]
                break
        plan.append(p)
    managers_query = CustomUser.objects.filter(id__in=managers_ids).order_by('pk')

    return managers_query, managers_ids, plan


# @func_time
def _get_managers(year: int, month: int) -> (QuerySet, list, list):
    """
    Getting Queryset of managers and list of managers plans

    :return: Queryset, list
    """
    if year != timezone.now().year or month != datetime.now().month:
        next_month = get_next_month(year, month)
        managers, manager_ids, plan = get_logged_managers(next_month)
    else:
        manager_ids = CustomUser.objects.filter(Q(partner_role__isnull=False) | Q(
            disciples_deals__isnull=False) | Q(
            partner_disciples_deals__isnull=False)).distinct().values_list('id', flat=True)
        managers = CustomUser.objects.filter(id__in=manager_ids).order_by('pk')
        plan = _get_managers_plan(managers)
        manager_ids = sorted(list(manager_ids))

    return managers, manager_ids, plan


# @func_time
def get_logged_partners(next_month: str) -> QuerySet:
    raw = """
          SELECT (SELECT pl.id FROM partnership_partnershiplogs pl WHERE p.id = pl.partner_id AND
          pl.log_date < '%s-01'
          ORDER BY log_date DESC LIMIT 1
          ) p_log_id
          FROM partnership_partnership p ORDER BY p.id;
          """ % next_month

    with connection.cursor() as connect:
        connect.execute(raw)
        logged_ids = [k[0] for k in connect.fetchall()]

    logged_queryset = PartnershipLogs.objects.filter(id__in=logged_ids)

    return logged_queryset


# @func_time
def get_logged_church_partners(next_month: str) -> QuerySet:
    raw = """
          SELECT (SELECT pl.id FROM partnership_churchpartnerlog pl WHERE p.id = pl.partner_id AND
          pl.log_date < '%s-01'
          ORDER BY log_date DESC LIMIT 1
          ) p_log_id
          FROM partnership_churchpartner p ORDER BY p.id;
          """ % next_month

    with connection.cursor() as connect:
        connect.execute(raw)
        logged_ids = [k[0] for k in connect.fetchall()]

    logged_queryset = ChurchPartnerLog.objects.filter(id__in=logged_ids)

    return logged_queryset


# @func_time
def _get_partners(year: int, month: int) -> (QuerySet, QuerySet):
    partners = Partnership.objects.all()
    church_partners = ChurchPartner.objects.all()

    if year != timezone.now().year or month != datetime.now().month:
        next_month = get_next_month(year, month)
        partners = get_logged_partners(next_month)
        church_partners = get_logged_church_partners(next_month)
    return partners, church_partners


# @func_time
def _get_managers_names(queryset: QuerySet) -> list:
    return list(queryset.annotate(full_name=Concat(
        'last_name', V(' '), 'first_name', V(' '), 'middle_name')).values(
        'full_name', 'id').order_by('pk'))


# @func_time
def _get_total_partners(partners, managers):
    s = dict(Counter(list(partners.order_by().values_list('responsible', flat=True))))
    return [s.get(m.pk, 0) for m in managers]


# @func_time
def _get_active_partners(partners, managers):
    s = dict(Counter(list(partners.filter(is_active=True).order_by().values_list('responsible', flat=True))))
    return [s.get(m.pk, 0) for m in managers]


# @func_time
def _get_potential_sum(partners, managers):
    s = list(partners.order_by().values('responsible', 'value'))
    return [sum([f['value'] for f in filter(lambda z: z['responsible'] == m.pk, s)]) for m in managers]


# @func_time
def _get_total_church_partners(partners, managers):
    s = dict(Counter(list(partners.order_by().values_list('responsible', flat=True))))
    return [s.get(m.pk, 0) for m in managers]


# @func_time
def _get_active_church_partners(partners, managers):
    s = dict(Counter(list(partners.filter(is_active=True).order_by().values_list('responsible', flat=True))))
    return [s.get(m.pk, 0) for m in managers]


# @func_time
def _get_church_potential_sum(partners, managers):
    s = list(partners.order_by().values('responsible', 'value'))
    return [sum([f['value'] for f in filter(lambda z: z['responsible'] == m.pk, s)]) for m in managers]


# @func_time
def get_managers_stats(year: int, month: int) -> list:
    managers_query, managers_ids, plan = _get_managers(year, month)  # QuerySet, list, list
    partners, church_partners = _get_partners(year, month)  # QuerySet, QuerySet

    managers_data = _get_managers_names(managers_query)  # list
    managers = [{
        # Making queries from Partnership model
        'sum_pay': x[0] or 0,
        'sum_pay_tithe': x[1] or 0,
        'sum_pay_church': x[2] or 0,
        'sum_deals': x[3] or 0,
        'sum_church_deals': x[4] or 0,
        'manager': x[5],
        'user_id': x[6],
        # Making queries from PartnershipLoUntitled Diagram.xmlgs model if requested period not in this month
        'total_partners': x[7] or 0,
        'active_partners': x[8] or 0,
        'potential_sum': x[9] or 0,
        'total_church_partners': x[10] or 0,
        'active_church_partners': x[11] or 0,
        'church_potential_sum': x[12] or 0,
        'plan': x[13] or 0,

    } for x in zip(
        # payments
        _get_sum_pay(year, month, deal_type=Deal.DONATION),  # list
        _get_sum_pay(year, month, deal_type=Deal.TITHE),  # list
        _get_sum_church_pay(year, month),  # list
        # deals
        _get_sum_deals(managers_query, year, month),  # list
        _get_sum_church_deals(managers_query, year, month),  # list
        # managers
        [p['full_name'] for p in managers_data],
        [p['id'] for p in managers_data],
        # partners
        _get_total_partners(partners, managers_query),
        _get_active_partners(partners, managers_query),
        _get_potential_sum(partners, managers_query),
        # church partners
        _get_total_church_partners(church_partners, managers_query),
        _get_active_church_partners(church_partners, managers_query),
        _get_church_potential_sum(church_partners, managers_query),
        plan,
    )]
    managers = [manager for manager in managers if (
            manager['potential_sum'] != 0 or
            manager['sum_pay'] != 0 or
            manager['sum_pay_church'] != 0 or
            manager['sum_pay_tithe'] != 0)]
    return managers


def get_managers_stats_cached(year: int, month: int) -> tuple:
    month_code = encode_month(year, month)
    try:
        ms = ManagersSummaryCache()
        stats, last_update = ms.get(month_code)
        if not stats:
            managers_summary.apply_async(args=(month_code,))
            stats = get_managers_stats(year, month)
    except Exception as err:
        logger.warning(err)
        managers_summary.apply_async(args=(month_code,))
        stats = get_managers_stats(year, month)
        last_update = timezone.now()
    return stats, last_update
