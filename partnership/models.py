# -*- coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict
from datetime import date

from django.db import models
from django.db.models import Sum
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Partnership(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='partnership')
    responsible = models.ForeignKey('self', related_name='disciples', null=True, blank=True, on_delete=models.SET_NULL)
    value = models.IntegerField()
    date = models.DateField(default=date.today)
    is_responsible = models.BooleanField(default=False)

    def __str__(self):
        return self.fullname

    @property
    def fullname(self):
        return self.user.fullname

    @property
    def common(self):
        return ['Пользователь', 'Ответственный', 'Сумма', 'Количество сделок', 'Итого']

    @property
    def result_value(self):
        if not self.is_responsible:
            deals = self.deals.aggregate(sum_deals=Sum('value'))
        else:
            deals = self.disciples.aggregate(sum_deals=Sum('deals__value'))
        if deals['sum_deals']:
            value = deals['sum_deals']
        else:
            value = 0
        return value

    @property
    def deals_count(self):
        count = self.deals.count()
        return count

    #
    # @property
    # def count(self):
    #     return self.deals_count

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
        l['user'] = d

        d = OrderedDict()
        # if not self.is_responsible:
        if self.responsible:
            d['value'] = self.responsible.user.get_full_name()
        else:
            d['value'] = ''
        # else:
        #     d['value'] = ''
        l['responsible'] = d

        d = OrderedDict()
        # if not self.is_responsible:
        if self.responsible:
            d['value'] = self.responsible.id
        else:
            d['value'] = None
        # else:
        #     d['value'] = None
        l[u'responsible_id'] = d

        d = OrderedDict()
        d['value'] = self.value
        l['value'] = d

        d = OrderedDict()
        d['value'] = self.deals_count
        l['count'] = d

        if self.is_responsible:
            d = OrderedDict()
            d['value'] = self.disciples.count()
            l['Количество партнеров'] = d
        else:
            pass

        d = OrderedDict()
        d['value'] = self.result_value
        d['type'] = 'i'
        d['change'] = False
        d['verbose'] = 'Итого'
        l['result_value'] = d
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


@python_2_unicode_compatible
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

    def __str__(self):
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
        l['id'] = d

        d = OrderedDict()
        d['value'] = self.partnership.user.get_full_name()
        d['title'] = "Клиент"
        l['fullname'] = d

        d = OrderedDict()
        if self.partnership.responsible:
            d['value'] = self.partnership.responsible.user.get_full_name()
        else:
            d['value'] = ""
        d['title'] = "Ответственный"
        l['responsible'] = d

        d = OrderedDict()
        d['value'] = self.date
        d['title'] = "Дата"
        l['date'] = d

        d = OrderedDict()
        d['value'] = self.value
        d['title'] = "Сумма"
        l['value'] = d

        d = OrderedDict()
        d['value'] = self.description
        d['title'] = "Описание"
        l['description'] = d

        d = OrderedDict()
        if self.done:
            d['value'] = "done"
        else:
            if self.expired:
                d['value'] = "expired"
            else:
                d['value'] = "undone"
        d['title'] = "Статус"
        l['status'] = d

        return l
