# -*- coding: utf-8
from __future__ import unicode_literals

import logging
from datetime import datetime, date
from decimal import Decimal

from edem.settings.celery import app
from partnership.models import Partnership, Deal

logger = logging.getLogger(__name__)


# def partnerships_deactivate():
#     from django.db.models import Count
#
#     valid_partners = Partnership.objects.annotate(count=Count('deals')).filter(count__gte=3)
#
#     def generate_partner_list(queryset):
#         for partner in queryset:
#             value = False
#             for deal in partner.deals.order_by('-date_created')[:3]:
#                 if not deal.expired:
#                     pass
#                 else:
#                     value = True
#             if not value:
#                 yield (partner.id)
#
#     return Partnership.objects.filter(id__in=generate_partner_list(valid_partners)).update(is_active=False)


class DealKeyError(Exception):
    pass


def partnerships_deactivate_raw():

    def make_partners_list(key='done'):

        if key not in ['done', 'expired']:
            raise DealKeyError('Invalid key')

        raw = """
        SELECT "partnership_partnership"."id",
        (SELECT array_agg(U0.%s)
        FROM "partnership_deal" U0
        WHERE U0.id IN (SELECT U1.id
        FROM "partnership_deal" U1
        WHERE U1."partnership_id" = ("partnership_partnership"."id")
        ORDER BY U1.date_created desc LIMIT 3)
        GROUP BY U0."partnership_id") AS "value"
        FROM "partnership_partnership";
        """ % key

        qs = Partnership.objects.raw(raw)
        partners_list = [p for p in list(qs) if p.value and len(p.value) == 3]
        if key == 'done':
            partners_list = [partner.id for partner in partners_list if not any(partner.value)]
        if key == 'expired':
            partners_list = [partner.id for partner in partners_list if all(partner.value)]

        return partners_list

    partners_to_deactivate = set(make_partners_list(key='done')) & set(make_partners_list(key='expired'))
    Partnership.objects.filter(id__in=partners_to_deactivate).update(is_active=False)


@app.task(name='create_new_deals')
def create_new_deals():
    try:
        partnerships_deactivate_raw()
    except DealKeyError as err:
        logger.error(err)
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    partnerships_without_deals = Partnership.objects \
        .filter(is_active=True) \
        .exclude(deals__date_created__month=current_month, deals__date_created__year=current_year) \
        .exclude(value=Decimal(0))
    for partnership in partnerships_without_deals:
        Deal.objects.create(partnership=partnership, value=partnership.value)


@app.task(name='deals_to_expired')
def deals_to_expired():
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    expired_deals = Deal.objects.filter(date_created__lt=date(current_year, current_month, 1), expired=False,
                                        done=False)
    expired_deals.update(expired=True)
