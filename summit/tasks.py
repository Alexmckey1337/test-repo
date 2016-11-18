# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from edem.celery import app
from summit.utils import generate_ticket
from .resources import make_table


@app.task(name='generate')
def generate():
    make_table()
    return True


@app.task(ignore_relust=True, max_retries=10, default_retry_delay=10)
def send_ticket(summit_anket):
    template_name = 'email/summit_ticket.html'
    ctx = {}
    main_email = settings.EMAIL_HOST_USER or ''
    recipient_list = [summit_anket.user.email]

    html_template = get_template(template_name)
    subject = ctx.get('subject', 'Билет')
    message = ctx.get('message', 'Билен на саммит {}'.format(summit_anket.summit))
    from_email = 'Билет <{email}>'.format(email=main_email)
    html_message = html_template.render(ctx)

    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list)
    mail.attach_alternative(html_message, 'text/html')

    mail.attach('{} ({}).pdf'.format(
        summit_anket.user.fullname, summit_anket.code),
        generate_ticket(summit_anket.code),
        'application/pdf')

    mail.send()
