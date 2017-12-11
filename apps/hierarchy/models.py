# -*- coding: utf-8
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models


@python_2_unicode_compatible
class Department(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Hierarchy(models.Model):
    title = models.CharField(max_length=50, unique=True)
    level = models.IntegerField()

    class Meta:
        ordering = ['level']

    def __str__(self):
        return self.title
