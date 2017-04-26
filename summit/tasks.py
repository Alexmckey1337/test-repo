# -*- coding: utf-8
from __future__ import unicode_literals

from io import BytesIO
from json import dumps

import redis
from channels import Group
from dbmail import send_db_mail
from django.core.files import File

from edem.settings.celery import app
from summit.models import SummitAnket, SummitTicket
from summit.utils import generate_ticket, generate_ticket_by_summit


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
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.sadd('summit:ticket:{}'.format(ticket.owner.id), ticket_id)
        r.expire('summit:ticket:{}'.format(ticket.owner.id), 7 * 24 * 60 * 60)
    except Exception as err:
        print(err)
    Group("summit_{}_ticket".format(ticket.owner.id)).send({'text': dumps(data)})
