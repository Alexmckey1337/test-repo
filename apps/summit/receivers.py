import traceback

from dbmail.backends.mail import Sender as MailSender
from dbmail.signals import post_send, post_exception

from apps.summit.models import AnketEmail


def log_send_ticket_email(*args, **kwargs):
    anket = kwargs.get('anket')
    instance = kwargs.get('instance')
    if anket and instance:
        AnketEmail.objects.create(
            anket_id=anket.id,
            recipient=anket.user.email,
            subject=instance._subject,
            text=instance._message,
            error_message=''
        )


def log_error_send_ticket_email(*args, **kwargs):
    anket = kwargs.get('anket')
    instance = kwargs.get('instance')
    if anket and instance:
        AnketEmail.objects.create(
            anket_id=anket.id,
            recipient=anket.user.email,
            subject=instance._subject,
            text=instance._message,
            error_message=traceback.format_exc() or '',
            is_success=False
        )


post_send.connect(log_send_ticket_email, sender=MailSender)
post_exception.connect(log_error_send_ticket_email, sender=MailSender)
