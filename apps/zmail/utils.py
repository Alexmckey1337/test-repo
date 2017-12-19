from datetime import datetime

from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import Template, Context
from html2text import html2text

from apps.zmail.models import ZMailTemplate
from apps.zmail.signals import pre_send, post_send, post_exception


class Sender:
    def __init__(self, slug, email, template_context=None, from_email=None, signals_kw=None, **kwargs):
        self._slug = slug
        self._email = [email] if isinstance(email, str) else email

        self._template = ZMailTemplate.objects.get(slug=slug)
        self._context = template_context or {}

        self._subject = self._get_subject()
        self._message = self._get_message()
        self._from_email = from_email or self._template.from_email

        self._signals_kw = signals_kw or {}
        self._kwargs = kwargs

    def _render_template_field(self, field):
        return Template(getattr(self._template, field, '')).render(Context(self._context))

    def _get_subject(self):
        return self._render_template_field('subject')

    def _get_message(self):
        return self._render_template_field('message')

    def _get_connection(self):
        return get_connection(**self._template.get_auth())

    def _attach_files(self, mail):
        for file_object in self._template.files.all():
            mail.attach_file(file_object.filename.path)

    def _send(self):
        msg = EmailMultiAlternatives(
            self._subject, html2text(self._message),
            from_email=self._from_email, to=self._email,
            connection=self._get_connection(), **self._kwargs
        )
        msg.attach_alternative(self._message, "text/html")
        self._attach_files(msg)
        msg.send()

    def send(self):

        if self._template.is_active:
            try:
                pre_send.send(self.__class__, instance=self, **self._signals_kw)
                self._send()
                post_send.send(self.__class__, instance=self, **self._signals_kw)
                return 'OK'
            except Exception as exc:
                post_exception.send(self.__class__, instance=self, exc=exc, **self._signals_kw)
                raise


def send_zmail(slug, recipient, *args, **kwargs):
    from apps.zmail.defaults import (
        CELERY_QUEUE, SEND_MAX_TIME, ENABLE_CELERY)

    args = (slug, recipient) + args
    send_after = kwargs.pop('send_after', None)
    send_at_date = kwargs.pop('send_at_date', None)
    _use_celery = kwargs.pop('use_celery', ENABLE_CELERY)
    use_celery = ENABLE_CELERY and _use_celery
    queue = kwargs.pop('queue', CELERY_QUEUE)

    if use_celery is True:

        template = ZMailTemplate.objects.get(slug=slug)
        send_after = send_after if send_after else template.interval

        options = {
            'args': args, 'kwargs': kwargs,
            'queue': queue,
            'time_limit': kwargs.get('time_limit', SEND_MAX_TIME),
        }

        if send_at_date is not None and isinstance(send_at_date, datetime):
            options.update({'eta': send_at_date})
        if send_after is not None:
            options.update({'countdown': send_after})
        if template.is_active:
            from apps.zmail import tasks
            return tasks.send_zmail.apply_async(**options)
    else:
        return Sender(*args, **kwargs).send()
