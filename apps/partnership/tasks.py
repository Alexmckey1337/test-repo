# -*- coding: utf-8
from __future__ import unicode_literals

import logging
from datetime import datetime, date
from decimal import Decimal

from django.db.models import OuterRef, Exists

from edem.settings.celery import app
from apps.partnership.models import Partnership, Deal, ChurchDeal, ChurchPartner

logger = logging.getLogger(__name__)


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
    exists_deals = Deal.objects.filter(
        partnership=OuterRef('pk'),
        date_created__month=current_month,
        date_created__year=current_year)
    partnerships_without_deals = Partnership.objects \
        .annotate(deal_exist=Exists(exists_deals)) \
        .filter(is_active=True) \
        .exclude(deal_exist=True) \
        .exclude(value=Decimal(0))
    for partnership in partnerships_without_deals:
        Deal.objects.create(partnership=partnership, value=partnership.value)
    church_exists_deals = ChurchDeal.objects.filter(
        partnership=OuterRef('pk'),
        date_created__month=current_month,
        date_created__year=current_year)
    church_partnerships_without_deals = ChurchPartner.objects \
        .annotate(deal_exist=Exists(church_exists_deals)) \
        .filter(is_active=True) \
        .exclude(deal_exist=True) \
        .exclude(value=Decimal(0))
    for church_partner in church_partnerships_without_deals:
        ChurchDeal.objects.create(partnership=church_partner, value=church_partner.value)


@app.task(name='deals_to_expired')
def deals_to_expired():
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    expired_deals = Deal.objects.filter(date_created__lt=date(current_year, current_month, 1), expired=False,
                                        done=False)
    expired_deals.update(expired=True)

    church_expired_deals = ChurchDeal.objects.filter(date_created__lt=date(current_year, current_month, 1), expired=False,
                                              done=False)
    church_expired_deals.update(expired=True)
