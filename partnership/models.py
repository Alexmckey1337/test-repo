# -*- coding: utf-8
from __future__ import unicode_literals
from collections import OrderedDict
from datetime import date
from django.db.models import Sum, Count

from django.db import models


class Partnership(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='partnership')
    responsible = models.ForeignKey('self', related_name='disciples', null=True, blank=True, on_delete=models.SET_NULL)
    value = models.IntegerField()
    date = models.DateField(default=date.today)
    is_responsible = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.get_full_name()

    @property
    def fullname(self):
        return self.user.get_full_name()

    @property
    def common(self):
        return [u'Пользователь', u'Ответственный', u'Сумма', u'Количество сделок', u'Итого']


    @property
    def result_value(self):
        if not self.is_responsible:
            deals = Deal.objects.filter(partnership=self).all().aggregate(sum_deals=Sum('value'))
        else:
            deals = Deal.objects.filter(partnership__responsible=self).all().aggregate(sum_deals=Sum('value'))
        if deals['sum_deals']:
            value = deals['sum_deals']
        else:
            value = 0
        return value

    @property
    def deals_count(self):
        count = self.deals.count()
        return count

    @property
    def done_deals_count(self):
        count = self.deals.filter(done=True).count()
        return count

    @property
    def undone_deals_count(self):
        count = self.deals.filter(done=False, expired=False).count()
        return count

    @property
    def expired_deals_count(self):
        count = self.deals.filter(expired=True).count()
        return count


    @property
    def fields(self):
        l = self.user.fields
        d = OrderedDict()
        d['value'] = self.user.get_full_name()
        l[u'user'] = d

        d = OrderedDict()
        if not self.is_responsible:
            if self.responsible:
                d['value'] = self.responsible.user.get_full_name()
            else:
                d['value'] = ''
        else:
            d['value'] = ''
        l[u'responsible'] = d

        d = OrderedDict()
        d['value'] = self.value
        l[u'value'] = d

        d = OrderedDict()
        d['value'] = self.deals_count
        l[u'count'] = d

        if self.is_responsible:
            d = OrderedDict()
            d['value'] = self.disciples.count()
            l[u'Количество партнеров'] = d
        else:
            pass

        d = OrderedDict()
        d['value'] = self.result_value
        d['type'] = 'i'
        d['change'] = False
        d['verbose'] = u'Итого'
        l[u'result_value'] = d
        return l

    @property
    def deal_fields(self):
        l = OrderedDict()
        if self.is_responsible:
            deals = Deal.objects.filter(partnership__responsible=self).all()
        else:
            deals = Deal.objects.filter(partnership=self).all()
        l = list()
        for deal in deals:
            l.append(deal.fields)
        return l


class Deal(models.Model):
    date = models.DateField(null=True, blank=True)
    date_created = models.DateField(null=True, blank=True, auto_now_add=True)
    value = models.IntegerField()
    partnership = models.ForeignKey('partnership.Partnership', related_name="deals", unique_for_month='date_created')
    description = models.TextField(blank=True)
    done = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

    class Meta:
        ordering = ('date_created',)

    def __unicode__(self):
        return "%s : %s" % (self.partnership, self.date)

    @property
    def month(self):
        return '{}.{}'.format(self.date_created.year, self.date_created.month)

    @property
    def fields(self):
        l = OrderedDict()

        d = OrderedDict()
        d['value'] = self.id
        d['title'] = "Идентификатор сделки"
        l[u'id'] = d

        d = OrderedDict()
        d['value'] = self.partnership.user.get_full_name()
        d['title'] = "Клиент"
        l[u'fullname'] = d

        d = OrderedDict()
        if self.partnership.responsible:
            d['value'] = self.partnership.responsible.user.get_full_name()
        else:
            d['value'] = ""
        d['title'] = "Ответственный"
        l[u'responsible'] = d

        d = OrderedDict()
        d['value'] = self.date
        d['title'] = "Дата"
        l[u'date'] = d

        d = OrderedDict()
        d['value'] = self.value
        d['title'] = "Сумма"
        l[u'value'] = d

        d = OrderedDict()
        d['value'] = self.description
        d['title'] = "Описание"
        l[u'description'] = d


        d = OrderedDict()
        if self.done:
            d['value'] = u"done"
        else:
            if self.expired:
                d['value'] = u"expired"
            else:
                d['value'] = u"undone"
        d['title'] = "Статус"
        l[u'status'] = d

        return l



