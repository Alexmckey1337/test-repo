# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime, date

from django.core.exceptions import ObjectDoesNotExist

from edem.celery import app
from partnership.models import Partnership, Deal


@app.task(name='create_new_deals')
def create_new_deals():
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    partnerships_without_deals = Partnership.objects.exclude(deals__date_created__month=current_month,
                                                             deals__date_created__year=current_year)

    for partnership in partnerships_without_deals:
        deal = Deal(partnership=partnership, value=partnership.value)
        try:
            previous_deal = Deal.objects.filter(partnership=partnership).latest('date')
        except ObjectDoesNotExist:
            pass
        else:
            deal.date = previous_deal.date
        finally:
            deal.save()


@app.task(name='deals_to_expired')
def deals_to_expired():
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    expired_deals = Deal.objects.filter(date_created__lt=date(current_year, current_month, 1), expired=False,
                                        done=False)
    expired_deals.update(expired=True)
