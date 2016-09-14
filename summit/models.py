# -*- coding: utf-8
from __future__ import unicode_literals
from django.db import models
from collections import OrderedDict
from datetime import date

class SummitType(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название саммита')
    image = models.ImageField(upload_to='summit_type/images/', null=True, blank=True)

    def __unicode__(self):
        return self.title

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''


class Summit(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.ForeignKey('SummitType', related_name='summits', blank=True, null=True)
    description = models.CharField(max_length=255, verbose_name='Описание',
                                   blank=True, null=True)

    def __unicode__(self):
        return '%s %s' % (self.type.title, self.start_date)

    @property
    def title(self):
        return self.type.title


class SummitAnket(models.Model):
    user = models.ForeignKey('account.CustomUser',
                             related_name='summit_ankets',
                             )
    summit = models.ForeignKey('Summit',
                               related_name='ankets',
                               verbose_name='Саммит',
                               blank=True,
                               null=True)
    value = models.PositiveSmallIntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=8, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    pastor = models.CharField(max_length=255, blank=True, null=True)
    bishop = models.CharField(max_length=255, blank=True, null=True)
    sotnik = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(default=date.today())
    department = models.CharField(max_length=255, blank=True, null=True)
    protected = models.BooleanField(default=False)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    responsible = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=12, blank=True, null=True)
    retards = models.BooleanField(default=False)
    class Meta:
        unique_together = (('user', 'summit'),)

    def __unicode__(self):
        return '%s %s' % (self.user.fullname, self.summit.type.title)

    @property
    def info(self):
        d = OrderedDict()
        d['value'] = '0'
        if self.value:
            d['value'] = self.value
        d['title'] = u"Информация про оплату"
        d['verbose'] = 'money_info'
        d['summit_title'] = ''
        d['summit_type_id'] = self.summit.type.id
        d['summit_anket_id'] = self.id
        d[u'description'] = self.description
        if self.summit.title:
            d['summit_title'] = self.summit.title
        d['start_date'] = ''
        if self.summit.start_date:
            d['start_date'] = self.summit.start_date
        l = self.user.fields
        l[u'money_info'] = d
        d = OrderedDict()
        d[u'value'] = self.description
        d['verbose'] = 'description'
        l[u'description'] = d
        return l

    @property
    def common(self):
        l = OrderedDict([('Оплата', 'money_info'),
                        ('Примечание', 'description'),
                         ])
        return l
