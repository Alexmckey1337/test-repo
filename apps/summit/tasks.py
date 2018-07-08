from datetime import datetime
from io import BytesIO
from json import dumps
from time import sleep, time

import pytz
import requests
from celery.result import AsyncResult
from channels import Group
from django.conf import settings
from django.core.files import File

from apps.notification.backend import RedisBackend
from apps.summit.models import SummitAnket, SummitTicket
from apps.summit.utils import SummitTicketPDF
from apps.zmail.models import ZMailTemplate
from apps.zmail.utils import send_zmail
from edem.settings.celery import app


@app.task(max_retries=10, default_retry_delay=10 * 60)
def create_ticket(profile_id, code, fullname):
    attach = SummitTicketPDF([profile_id]).generate_pdf()
    profile = SummitAnket.objects.get(id=profile_id)

    pdf_name = '{} ({}).pdf'.format(fullname, code)
    profile.ticket.save(pdf_name, File(BytesIO(attach)))


@app.task(max_retries=0)
def create_tickets(ankets):
    for anket in ankets:
        create_ticket.delay(anket.get('id'), anket.get('code'), anket.get('fullname'))


@app.task(ignore_result=True, max_retries=0)
def send_tickets(anket_ids):
    profiles = SummitAnket.objects.in_bulk(anket_ids)
    for profile in profiles.values():
        if profile.summit.zmail_template and profile.user.email:
            attach = SummitTicketPDF([profile.pk]).generate_pdf()
            pdf_name = '{} ({}).pdf'.format(profile.user.fullname, profile.code)
            send_zmail(
                profile.summit.zmail_template.slug,
                profile.user.email,
                template_context={'anket': profile},
                attachments=[(pdf_name, attach, 'application/pdf')],
                signals_kw={'anket': profile}
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
        'time': pytz.utc.localize(datetime.fromtimestamp(error_time)).strftime('%d.%m.%Y %H:%M:%S%z'),
        'user_id': sender_id,
    }
    Group("summit_email_code_error_{}".format(sender_id)).send({'text': dumps(data)})


@app.task(max_retries=0)
def send_email_with_code(profile_id, sender_id, countdown=0):
    profile = SummitAnket.objects.select_related('summit__zmail_template', 'user').get(pk=profile_id)
    template = profile.summit.zmail_template
    email = profile.user.email
    if template and email:
        try:
            pdf = SummitTicketPDF([profile.pk]).generate_pdf()
            task = send_zmail(
                template.slug,
                email,
                template_context={'profile': profile},
                attachments=[('ticket.pdf', pdf, 'application/pdf')],
                signals_kw={'anket': profile},
                send_after=countdown,
                max_retries=0
            )
            try:
                r = RedisBackend()
                r.sadd('summit:email:sending:{}:{}'.format(profile.summit_id, profile_id), task.id)
                r.expire('summit:email:sending:{}:{}'.format(profile.summit_id, profile), 30 * 24 * 60 * 60)
            except Exception as err:
                print(err)
            # if isinstance(result, AsyncResult):
            #     check_send_email_with_code_state.apply_async(args=[result.id, profile_id, sender_id])
        except Exception:
            send_error(profile_id, sender_id)


@app.task(max_retries=0)
def send_email_with_schedule(profile_id, sender_id, template_slug, countdown=0):
    profile = SummitAnket.objects.select_related('summit', 'user').get(pk=profile_id)
    template = ZMailTemplate.objects.get(slug=template_slug)
    email = profile.user.email
    if template and email:
        try:
            task = send_zmail(
                template.slug,
                email,
                template_context={'profile': profile},
                send_after=countdown,
                max_retries=0
            )
            try:
                r = RedisBackend()
                r.sadd('summit:schedule:sending:{}:{}'.format(profile.summit_id, profile_id), task.id)
                r.expire('summit:schedule:sending:{}:{}'.format(profile.summit_id, profile), 30 * 24 * 60 * 60)
            except Exception as err:
                print(err)
                # if isinstance(result, AsyncResult):
                #     check_send_email_with_code_state.apply_async(args=[result.id, profile_id, sender_id])
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
def check_send_email_with_code_state(task_id, profile_id, sender_id):
    result = AsyncResult(task_id)

    while not result.ready():
        sleep(1)

    if result.failed():
        send_error(profile_id, sender_id)


@app.task(max_retries=10, default_retry_delay=10 * 60)
def generate_tickets(summit_id, profile_ids, profile_codes, ticket_id, filename=''):
    pdf = SummitTicketPDF(profile_ids).generate_pdf()
    pdf_name = filename or '{}_{}-{}'.format(summit_id, min(profile_codes), max(profile_codes))
    pdf_name += '.pdf'

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
