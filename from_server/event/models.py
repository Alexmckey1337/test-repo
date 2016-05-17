# -*- coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.utils import timezone

DAY_OF_THE_WEEK = {
    '1': _(u'Monday'),
    '2': _(u'Tuesday'),
    '3': _(u'Wednesday'),
    '4': _(u'Thursday'),
    '5': _(u'Friday'),
    '6': _(u'Saturday'),
    '7': _(u'Sunday'),
}
ATTR_TYPES = (
    ('s', 'string'),
    ('b', 'boolean'),
    ('i', 'integer'),
)

VERBOSE_FIELDS = {'Имя': 'user__first_name',
                  'Фамилия': 'user__last_name',
                  'Отчество': 'user__middle_name',
                  'Иерархия': 'user__hierarchy',
                  'Отдел': 'user__department',
                  'Страна': 'user__country',
                  'Город': 'user__city',
                  'Примечание': 'description',
                  'Явка': 'check'}

weekday = timezone.now().weekday() + 1


class DayOfTheWeekField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(DAY_OF_THE_WEEK.items()))
        kwargs['max_length'] = 1
        super(DayOfTheWeekField, self).__init__(*args, **kwargs)



class Event(models.Model):
    title = models.CharField(max_length=100, default='', unique=True)
    day = DayOfTheWeekField(null=True)
    users = models.ManyToManyField('account.CustomUser',
                                   through='Participation',
                                   through_fields=('event', 'user'),
                                   blank=True,
                                   related_name='events')
    active = models.BooleanField(default=True)
    cyclic = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "События"

    def __unicode__(self):
        return self.title


from report.models import UserReport


class Participation(models.Model):
    user = models.ForeignKey('account.CustomUser', related_name='participations')
    event = models.ForeignKey('event.Event', related_name='participations')
    check = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Участия"


    @property
    def common(self):
        l = VERBOSE_FIELDS
        return l

    @property
    def fields(self):
        
        l = self.user.fields
        l['id'] = self.user.id
        d = OrderedDict()
        d['value'] = self.description
        d['type'] = 's'
        d['change'] = True
        d['verbose'] = 'description'
        l[u'Примечание'] = d
        d = OrderedDict()
        if self.user.hierarchy.level > 1:
            report = UserReport.objects.filter(user=self.user, event=self.event).last()
            d['value'] = report.count
            d['type'] = 's'
            d['change'] = False
        else:
            d['value'] = self.check
            d['type'] = 'b'
            d['change'] = True 
        d['verbose'] = 'check'
        l[u'Явка'] = d
        return l


