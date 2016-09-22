# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class NotificationTheme(models.Model):
    title = models.CharField(max_length=100)
    birth_day = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Notification(models.Model):
    user = models.ForeignKey('account.CustomUser', null=True, blank=True)
    theme = models.ForeignKey(NotificationTheme, related_name='notifications')
    description = models.TextField()
    date = models.DateField(null=True, blank=True)
    common = models.BooleanField(default=True)
    system = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return '{} {}'.format(self.fullname, self.theme)

    @property
    def fullname(self):
        return self.user.get_full_name()

    @property
    def uid(self):
        return str(self.user.id)
