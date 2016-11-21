# -*- coding: utf-8
from __future__ import unicode_literals

from io import BytesIO

from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from edem.celery import app
from summit.models import AnketEmail
from summit.utils import generate_ticket
from .resources import make_table


@app.task(name='generate')
def generate():
    make_table()
    return True


@app.task(ignore_relust=True, max_retries=10, default_retry_delay=10)
def send_ticket(data):
    template_name = 'email/summit_ticket.html'
    main_email = settings.EMAIL_HOST_USER or ''

    recipient = data.get('email')
    anket_id = data.get('anket_id')
    summit_name = data.get('summit_name')
    fullname = data.get('fullname')
    code = data.get('code')

    ctx = {
        'fullname': fullname,
        'message': 'Поздравляю тебя, {}!\nТебе пришел билет на саммит,'
                   'его необходимо распечатать и предъявить при входе в Палац Украина.'.format(fullname)
    }

    html_template = get_template(template_name)
    subject = ctx.get('subject', 'Билет на саммит')
    message = ctx.get('message', 'Билен на саммит')
    from_email = 'Саммит <{email}>'.format(email=main_email)
    html_message = html_template.render(ctx)

    mail = EmailMultiAlternatives(subject, message, from_email, [recipient])
    mail.attach_alternative(html_message, 'text/html')

    attach = generate_ticket(code)
    pdf_name = '{} ({}).pdf'.format(fullname, code)
    mail.attach(pdf_name, attach, 'application/pdf')

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
