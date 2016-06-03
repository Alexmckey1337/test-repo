from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    phone_code = models.CharField(max_length=5, default="", blank=True, null=True)

    def __unicode__(self):
        return self.title


class Region(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    country = models.ForeignKey(Country)

    def __unicode__(self):
        return self.title


class City(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    region = models.ForeignKey(Region, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    def __unicode__(self):
        return self.title
