# -*- coding: utf-8
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models


@python_2_unicode_compatible
class Status(models.Model):
    title = models.CharField(max_length=20, unique=True)
    user = models.ManyToManyField('account.CustomUser', related_name='statuses')

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Division(models.Model):
    title = models.CharField(max_length=50, unique=True)
    user = models.ManyToManyField('account.CustomUser', related_name='divisions')

    def __str__(self):
        return self.title
