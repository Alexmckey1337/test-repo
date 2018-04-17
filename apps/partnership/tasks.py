import logging
import requests
from datetime import date
from decimal import Decimal

from django.db.models import OuterRef, Exists
from django.utils import timezone

from edem.settings.celery import app
from apps.partnership.models import Partnership, Deal, ChurchDeal, ChurchPartner, TelegramUser, TelegramGroup
from apps.account.models import CustomUser
from rest_framework.generics import get_object_or_404


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
    telegram_users_to_deactivate(partners_to_deactivate)


def telegram_users_to_deactivate(deactivate_partners):
    users = CustomUser.objects.filter(partners__in=deactivate_partners,
                                      telegram_users__isnull=False)

    for user in users:
        if not user.partners.filter(is_active=True).exists():
            telegram_user = get_object_or_404(TelegramUser, user=user)
            if telegram_user.is_active:
                telegram_user.is_active = False
                telegram_user.synced = False
                telegram_user.save()


@app.task(name='telegram_users_to_kick')
def telegram_users_to_kick():
    users_to_kick = TelegramUser.objects.filter(synced=False)

    if users_to_kick:
        for telegram_user in users_to_kick:
            kick_from_telegram.apply_async(args=[telegram_user.id])


@app.task(name='kick_from_telegram')
def kick_from_telegram(telegram_user_id):
    telegram_user = TelegramUser.objects.get(id=telegram_user_id)

    r = requests.delete('http://hola.nodeads.com:8888/bot/partner/',
                        params={'user_id': telegram_user.telegram_id,
                                'chat_id': telegram_user.telegram_group.chat_id})

    if r.status_code == 200:
        telegram_user.synced = True
        telegram_user.save()
    else:
        print(r.status_code)


@app.task(name='create_new_deals')
def create_new_deals():
    try:
        partnerships_deactivate_raw()
    except DealKeyError as err:
        logger.error(err)
    current_date = timezone.now()
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
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year

    expired_deals = Deal.objects.filter(date_created__lt=date(current_year, current_month, 1), expired=False,
                                        done=False)
    expired_deals.update(expired=True)

    church_expired_deals = ChurchDeal.objects.filter(date_created__lt=date(current_year, current_month, 1),
                                                     expired=False, done=False)
    church_expired_deals.update(expired=True)


@app.task(name='trainee_group_members_deactivate')
def trainee_group_members_deactivate():
    trainee_group = TelegramGroup.objects.get(title='Trainees')
    trainees = TelegramUser.objects.filter(telegram_group=trainee_group).exclude(is_active=False)

    for trainee in trainees:
        if trainee.user.hierarchy.title != 'Стажёр':
            trainee.is_active = False
            trainee.synced = False
            trainee.save()


@app.task(name='vip_partners_group_members_deactivate')
def vip_partners_group_members_deactivate():
    vip_partners_group = TelegramGroup.objects.get(title='VIP_Partners')
    vip_partners = TelegramUser.objects.filter(telegram_group=vip_partners_group).exclude(is_active=False)
    print(vip_partners)
    for group_member in vip_partners:
        print(group_member)
        for partner_account in group_member.user.partners.filter(value__gte=12500):
            print(partner_account if partner_account else 'None')
            if not partner_account or partner_account.is_active:
                print('1')
                group_member.is_active = False
                group_member.synced = False
                group_member.save()
    # TO DO - FINISH THIS
