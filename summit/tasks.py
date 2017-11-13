# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime, timedelta
from io import BytesIO
from json import dumps
from time import sleep, time

import requests
from celery.result import AsyncResult
from channels import Group
from dbmail import send_db_mail, send_db_sms
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File

from edem.settings.celery import app
from notification.backend import RedisBackend
from summit.models import SummitAnket, SummitTicket, SummitAttend
from summit.utils import generate_ticket, generate_ticket_by_summit
from django.conf import settings


@app.task(ignore_result=True, max_retries=10, default_retry_delay=10 * 60)
def create_ticket(anket_id, code, fullname):
    attach = generate_ticket(code)
    anket = SummitAnket.objects.get(id=anket_id)

    pdf_name = '{} ({}).pdf'.format(fullname, code)
    anket.ticket.save(pdf_name, File(BytesIO(attach)))


@app.task(ignore_result=True, max_retries=0)
def create_tickets(ankets):
    for anket in ankets:
        create_ticket.delay(anket.get('id'), anket.get('code'), anket.get('fullname'))


@app.task(ignore_result=True, max_retries=0)
def send_tickets(anket_ids):
    ankets = SummitAnket.objects.in_bulk(anket_ids)
    for anket in ankets.values():
        if anket.summit.mail_template and anket.user.email:
            attach = generate_ticket(anket.code)
            pdf_name = '{} ({}).pdf'.format(anket.user.fullname, anket.code)
            send_db_mail(
                anket.summit.mail_template.slug,
                anket.user.email,
                anket,
                attachments=[(pdf_name, attach, 'application/pdf')],
                signals_kwargs={'anket': anket}
            )


def send_error(profile_id, sender_id):
    error_time = int(time())
    try:
        r = RedisBackend()
        r.sadd('summit:email:code:error:{}'.format(sender_id), '{}:{}'.format(profile_id, error_time))
        r.expire('summit:email:code:error:{}'.format(sender_id), 3 * 24 * 60 * 60)
    except Exception as err:
        print(err)
    profile = SummitAnket.objects.get(pk=profile_id)
    data = {
        'type': 'SUMMIT_EMAIL_CODE_ERROR',
        'profile_id': profile_id,
        'profile_url': profile.get_absolute_url(),
        'profile_title': profile.fullname,
        'time': datetime.fromtimestamp(error_time).strftime('%d.%m.%Y %H:%M'),
        'user_id': sender_id,
    }
    Group("summit_email_code_error_{}".format(sender_id)).send({'text': dumps(data)})


@app.task(max_retries=0)
def send_email_with_code(profile_id, sender_id):
    profile = SummitAnket.objects.select_related('summit__mail_template', 'user').get(pk=profile_id)
    template = profile.summit.mail_template
    email = profile.user.email
    if template and email:
        try:
            pdf = generate_ticket(profile.code)
            result = send_db_mail(
                template.slug,
                email,
                {'profile': profile},
                attachments=[('ticket.pdf', pdf, 'application/pdf')],
                signals_kwargs={'anket': profile}
            )
            if isinstance(result, AsyncResult):
                check_send_email_with_code_state.apply_async(args=[result.id, profile_id, sender_id])
        except Exception:
            send_error(profile_id, sender_id)


def get_send_pulse_access_key():
    url = 'https://api.sendpulse.com/oauth/access_token'
    keys = {'client_id': settings.SEND_PULSE_CLIENT_ID,
            'client_secret': settings.SEND_PULSE_CLIENT_SECRET,
            'grant_type': settings.SEND_PULSE_GRANT_TYPE}

    data = requests.post(url, keys)
    data = data.json()
    access_key = {
        "Authorization": "%s %s" % (data.get('token_type'), data.get('access_token'))
    }

    return access_key


@app.task(ignore_result=True, max_retries=0)
def send_sms_with_code(profile_id, sender_id):
    profile = SummitAnket.objects.get(pk=profile_id)
    template = profile.summit.sms_template
    # recipient = profile.user.phone_number
    recipient = "380932875260"

    r = {
        "recipients": [
            recipient
        ],
        "message": "Текст Viber сообщения",
        "message_live_time": 60,
        "sender_id": 1,
        "send_date": "now",
        "additional": {
            "resend_sms": {
                "status": True,
                "sms_text": "Текст SMS сообщения",
                "sms_sender_name": "VOTV"
            }
        }
    }

    if template and recipient:
        try:
            result = send_db_sms(
                slug=template.slug,
                recipient=recipient,
            )
            if isinstance(result, AsyncResult):
                check_send_email_with_code_state.apply_async(args=[result.id, profile_id, sender_id])
        except Exception:
            send_error(profile_id, sender_id)


@app.task(ignore_result=True, max_retries=0)
def check_send_email_with_code_state(task_id, profile_id, sender_id):
    result = AsyncResult(task_id)

    while not result.ready():
        print(result.status)
        sleep(1)

    if result.failed():
        send_error(profile_id, sender_id)


@app.task(ignore_result=True, max_retries=10, default_retry_delay=10 * 60)
def generate_tickets(summit_id, ankets, ticket_id):
    pdf = generate_ticket_by_summit(ankets)
    pdf_name = '{}_{}-{}.pdf'.format(
        summit_id, min(ankets, key=lambda a: int(a[1]))[1], max(ankets, key=lambda a: int(a[1]))[1])

    ticket = SummitTicket.objects.get(id=ticket_id)

    ticket.attachment.save(pdf_name, File(BytesIO(pdf)))
    ticket.status = SummitTicket.COMPLETE
    ticket.save()

    data = {
        'type': 'SUMMIT_TICKET',
        'summit_id': summit_id,
        'user_id': ticket.owner.id,
        'ticket_id': ticket_id,
        'ticket_title': ticket.title,
        'ticket_url': ticket.get_absolute_url(),
        'file': ticket.attachment.url
    }
    try:
        r = RedisBackend()
        r.sadd('summit:ticket:{}'.format(ticket.owner.id), ticket_id)
        r.expire('summit:ticket:{}'.format(ticket.owner.id), 7 * 24 * 60 * 60)
    except Exception as err:
        print(err)
    Group("summit_{}_ticket".format(ticket.owner.id)).send({'text': dumps(data)})


@app.task(name='get_palace_logs', ignore_result=True, max_retries=5, default_retry_delay=10)
def get_palace_logs():
    url = 'https://armspalace.esport.in.ua/m-ticket/gatelog/getLogs/'
    date_to = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_from = (datetime.now() - timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S')
    data = requests.get(url + '?dateFrom=' + date_from + '&dateTo=' + date_to)

    for _pass in data.json():
        date_time = datetime.strptime(_pass['date'], '%Y-%m-%d %H:%M:%S')
        try:
            anket = SummitAnket.objects.get(code=_pass['barcode'][4:])
        except ObjectDoesNotExist:
            continue
        SummitAttend.objects.get_or_create(
            anket=anket, date=date_time.date(), defaults={'time': date_time.time(),
                                                          'status': _pass['status']})
