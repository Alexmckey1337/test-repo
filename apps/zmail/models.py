import uuid

import os
import re
from django.db import models
from django.utils.translation import ugettext_lazy as _
from premailer import transform

CACHE_TTL = None
DEFAULT_FROM_EMAIL = None
UPLOAD_TO = 'zmail'


def app_installed(app):
    from django.conf import settings

    return app in settings.INSTALLED_APPS


if app_installed('tinymce'):
    try:
        from tinymce.models import HTMLField  # pragma: no flake8

    except ImportError:
        pass

if app_installed('ckeditor'):
    try:
        from ckeditor.fields import RichTextField as HTMLField

    except ImportError:
        pass


def _upload_mail_file(instance, filename):
    if instance is not None:
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (str(uuid.uuid4()), ext)
        return os.path.join(UPLOAD_TO, filename)


class ZMailAuth(models.Model):
    host = models.CharField(_('Host'), max_length=255)
    port = models.PositiveIntegerField(_('Port'))
    username = models.CharField(_('Username'), max_length=255, blank=True)
    password = models.CharField(_('Password'), max_length=255, blank=True)
    use_tls = models.BooleanField(_('Use TLS'), default=False)
    fail_silently = models.BooleanField(_('Fail silently'), default=False)

    def __str__(self):
        return '{}/{}'.format(self.username, self.host)

    class Meta:
        verbose_name = _('Mail auth settings')
        verbose_name_plural = _('Mail auth settings')


class ZMailTemplate(models.Model):
    name = models.CharField(_('Template name'), max_length=255)
    subject = models.CharField(_('Subject'), max_length=255)
    from_email = models.CharField(_('Message from'), max_length=255, default=DEFAULT_FROM_EMAIL, blank=True)
    auth = models.ForeignKey(
        ZMailAuth, on_delete=models.PROTECT, verbose_name=_('Auth credentials'),
        blank=True, null=True, default=None)
    message = HTMLField(_('Body'))
    slug = models.SlugField(
        _('Slug'), unique=True,
        help_text=_('Unique slug to use in code.'))
    is_active = models.BooleanField(_('Is active'), default=True)
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)
    interval = models.PositiveIntegerField(_('Send interval'), null=True, blank=True)

    def save(self, *args, **kwargs):
        self.message = transform(self.message)
        self.slug = re.sub(r'[^\w._-]', '', self.slug)
        super().save(*args, **kwargs)

    def get_auth(self):
        if self.auth:
            return {
                'host': self.auth.host,
                'port': self.auth.port,
                'username': str(self.auth.username),
                'password': str(self.auth.password),
                'use_tls': self.auth.use_tls,
                'fail_silently': self.auth.fail_silently
            }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Mail template')
        verbose_name_plural = _('Mail templates')


class ZMailAttachment(models.Model):
    template = models.ForeignKey(
        ZMailTemplate, on_delete=models.CASCADE, verbose_name=_('Template'), related_name='files')
    name = models.CharField(_('Name'), max_length=255)
    filename = models.FileField(_('File'), upload_to=_upload_mail_file)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Mail file')
        verbose_name_plural = _('Mail files')
