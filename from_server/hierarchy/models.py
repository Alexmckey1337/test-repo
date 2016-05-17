# -*- coding: utf-8
from __future__ import unicode_literals
from django.db import models
from collections import OrderedDict


class Department(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.title


class Hierarchy(models.Model):
    title = models.CharField(max_length=50, unique=True)
    level = models.IntegerField()

    class Meta:
        ordering = ['level']

    def __unicode__(self):
        return self.title


