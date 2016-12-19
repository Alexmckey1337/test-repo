# -*- coding: utf-8
from __future__ import unicode_literals

from io import BytesIO

from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import get_template

from edem.settings.celery import app
from summit.models import AnketEmail, SummitAnket
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
def send_tickets(ankets):
    for anket in ankets:
        email_data = {
            'anket_id': anket.get('id', ''),
            'email': anket.get('user__email', ''),
            'summit_name': '{} {}'.format(anket.get('summit__type__title', ''), anket.get('summit__start_date', '')),
            'fullname': '{} {} {}'.format(anket.get('user__first_name', ''),
                                          anket.get('user__last_name', ''),
                                          anket.get('user__middle_name', '')),
            'code': anket.get('code', ''),
            'ticket': anket.get('ticket', '')
        }
        send_ticket.delay(email_data)


@app.task(ignore_result=True, max_retries=10, default_retry_delay=10 * 60)
def send_ticket(data, force_ticket=False):
    template_name = 'email/summit_ticket.html'
    main_email = settings.EMAIL_HOST_USER or ''

    recipient = data.get('email')
    anket_id = data.get('anket_id')
    summit_name = data.get('summit_name')
    fullname = data.get('fullname')
    code = data.get('code')

    ctx = {
        'fullname': fullname,
        'message': 'Дорогой студент!'
                   'В этом письме находится твой электронный билет. Распечатай его и сохрани,'
                   'он будет твоим пропуском на все дни обучения на саммите. '
                   'В этом билете закодированы твои персональные данные. '
                   'До встречи на саммите!'
                   'С уважением Администрация саммита.'
    }

    auth_user = '4izmerenie@vo.org.ua'
    auth_password = 'natasha120821'

    html_template = get_template(template_name)
    subject = ctx.get('subject', 'Билет на саммит')
    message = ctx.get('message', 'Билен на саммит')
    from_email = 'Саммит 4 Измерение <{email}>'.format(email=auth_user)
    html_message = html_template.render(ctx)
    connection = get_connection(username=auth_user, password=auth_password)
    mail = EmailMultiAlternatives(subject, message, from_email, [recipient], connection=connection)
    mail.attach_alternative(html_message, 'text/html')

    anket = SummitAnket.objects.get(id=anket_id)
    # TODO crutch
    force_ticket = True
    if force_ticket or not data.get('ticket'):
        attach = generate_ticket(code)
        pdf_name = '{} ({}).pdf'.format(fullname, code)
        mail.attach(pdf_name, attach, 'application/pdf')
        anket.ticket.save(pdf_name, File(BytesIO(attach)))
    else:
        file = anket.ticket
        attach = file.read()
        pdf_name = '{} ({}).pdf'.format(fullname, code)
        mail.attach(pdf_name, attach, 'application/pdf')
        file.close()

    send = mail.send()
    if send > 0 and anket_id:
        email = AnketEmail.objects.create(
            anket_id=anket_id,
            recipient=recipient,
            subject=subject,
            text=message,
            html=html_message
        )
        email.attach.save(pdf_name, File(BytesIO(attach)))
