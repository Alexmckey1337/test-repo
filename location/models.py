from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)

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
    region = models.ForeignKey(Region)

    def __unicode__(self):
        return self.title
