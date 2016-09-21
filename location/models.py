# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Country(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    phone_code = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Region(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    country = models.ForeignKey(Country)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class City(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    region = models.ForeignKey(Region, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)

    def __str__(self):
        return self.title
