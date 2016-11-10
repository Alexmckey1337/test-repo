# -*- coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict
from datetime import date

from django.db import models
from django.db.models import Sum, Count
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Partnership(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='partnership')
    value = models.IntegerField()
    date = models.DateField(default=date.today)
    need_text = models.CharField(_('Need text'), max_length=300, blank=True)

    is_active = models.BooleanField(_('Is active?'), default=True)

    DIRECTOR, SUPERVISOR, MANAGER, PARTNER = 0, 1, 2, 3
    LEVELS = (
        (DIRECTOR, _('Director')),
        (SUPERVISOR, _('Supervisor')),
        (MANAGER, _('Manager')),
        (PARTNER, _('Partner')),
    )
    level = models.PositiveSmallIntegerField(_('Level'), choices=LEVELS, default=PARTNER)

    responsible = models.ForeignKey('self', related_name='disciples', limit_choices_to={'level__lte': MANAGER},
                                    null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.fullname

    @property
    def is_responsible(self):
        return self.level <= Partnership.MANAGER

    @property
    def fullname(self):
        return self.user.fullname

    @property
    def common(self):
        return ['Пользователь', 'Ответственный', 'Сумма', 'Количество сделок', 'Итого']

    @property
    def result_value(self):
        return self.deals.aggregate(sum_deals=Sum('value'))['sum_deals']

    @property
    def disciples_result_value(self):
        return self.disciples.aggregate(sum_deals=Sum('deals__value'))['sum_deals']

    @property
    def deals_count(self):
        return self.deals.count()

    @property
    def disciples_count(self):
        return self.disciples.aggregate(count=Count('deals'))['count']

    #
    # @property
    # def count(self):
    #     return self.deals_count

    @property
    def done_deals_count(self):
        if self.is_responsible:
            count = Deal.objects.filter(done=True, partnership__in=self.disciples.all()).count()
        else:
            count = self.deals.filter(done=True).count()
        return count

    @property
    def undone_deals_count(self):
        if self.is_responsible:
            count = Deal.objects.filter(done=False, expired=False, partnership__in=self.disciples.all()).count()
        else:
            count = self.deals.filter(done=False, expired=False).count()
        return count

    @property
    def expired_deals_count(self):
        if self.is_responsible:
            count = Deal.objects.filter(expired=True, partnership__in=self.disciples.all()).count()
        else:
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
    value = models.IntegerField(default=0)
    partnership = models.ForeignKey('partnership.Partnership', related_name="deals")
    description = models.TextField(blank=True)
    done = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

    date_created = models.DateField(null=True, blank=True, default=date.today)
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ('date_created',)

    def __str__(self):
        return "%s : %s" % (self.partnership, self.date)

    @property
    def month(self):
        if self.date_created:
            return '{}.{}'.format(self.date_created.year, self.date_created.month)
        return ''

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
