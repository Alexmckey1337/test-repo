# -*- coding: utf-8
from __future__ import unicode_literals

from io import BytesIO

from dbmail import send_db_mail
from django.core.files import File

from edem.settings.celery import app
from summit.models import SummitAnket
from summit.utils import generate_ticket
from .resources import make_table


@app.task(name='generate')
def generate():
    make_table()
    return True


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
