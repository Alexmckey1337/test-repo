from __future__ import unicode_literals
from django.db import models


class Status(models.Model):
    title = models.CharField(max_length=20, unique=True)
    user = models.ManyToManyField('account.CustomUser', related_name='statuses')

    def __unicode__(self):
        return self.title

