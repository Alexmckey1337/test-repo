# -*- coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone
from datetime import date
from django.db.models import signals
from django.dispatch import receiver
from collections import OrderedDict
from django.db.models import Sum
import datetime


DAY_OF_THE_WEEK = {
    '1': _(u'Monday'),
    '2': _(u'Tuesday'),
    '3': _(u'Wednesday'),
    '4': _(u'Thursday'),
    '5': _(u'Friday'),
    '6': _(u'Saturday'),
    '7': _(u'Sunday'),
}
weekday = timezone.now().weekday() + 1
default_date = timezone.now()


class DayOfTheWeekField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(DAY_OF_THE_WEEK.items()))
        kwargs['max_length'] = 1
        super(DayOfTheWeekField, self).__init__(*args, **kwargs)


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


def current_week():
    return datetime.date.today().isocalendar()[1]


class EventType(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/eventTypes/', null=True, blank=True)
    home = models.BooleanField(default=False)
    night = models.BooleanField(default=False)
    service = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    @property
    def event_count(self):
        return self.events.count()

    @property
    def last_event_date(self):
        last_event = self.events.last()
        return str(last_event.from_date)


class EventAnket(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='event_anket', )

    def __unicode__(self):
        return self.user.get_full_name()


class Week(models.Model):
    week = models.IntegerField(default=current_week, unique=True)
    from_date = models.DateField(default=date.today)
    to_date = models.DateField(default=date.today)

    def __unicode__(self):
        return unicode(self.week)


class Event(models.Model):
    week = models.ForeignKey(Week, null=True, blank=True)
    event_type = models.ForeignKey(EventType, related_name='events', blank=True, null=True)
    from_date = models.DateField(default=date.today)
    to_date = models.DateField(default=date.today)
    time = models.TimeField(default=timezone.now)
    users = models.ManyToManyField(EventAnket,
                                   through='Participation',
                                   through_fields=('event', 'user'),
                                   blank=True,
                                   related_name='events')

    class Meta:
        verbose_name_plural = "События"

    def __unicode__(self):
        return self.event_type.title

    @property
    def title(self):
        return self.event_type.title


class Participation(models.Model):
    user = models.ForeignKey(EventAnket, related_name='participations')
    event = models.ForeignKey(Event, related_name='participations')
    check = models.BooleanField(default=False)
    value = models.IntegerField(blank=True, null=True)
    result_value = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(default=0)
    count_as_leader = models.IntegerField(default=0)
    value_as_leader = models.IntegerField(default=0)


    class Meta:
        verbose_name_plural = "Участия"

    @property
    def uid(self):
        return self.user.user.id

    @property
    def hierarchy_chain(self):
        return self.user.user.hierarchy_chain

    @property
    def has_disciples(self):
        return self.user.user.has_disciples

    def get_count(self):
        if self.value:
            value = self.value
        else:
            value = 0
        if self.check:
            count = 1
        else:
            count = 0
        if self.user.user.has_disciples:
            sum_count = Participation.objects.filter(user__user__master=self.user.user, event=self.event).aggregate(Sum('count'))
            sum_value = Participation.objects.filter(user__user__master=self.user.user, event=self.event).aggregate(Sum('value'))
            count += sum_count.values()[0]
            value += sum_value.values()[0]
        self.result_value = value
        self.count = count
        self.save()
        return self.count

    def get_as_leader_count(self):
        if self.value:
            value = self.value
        else:
            value = 0
        if self.check:
            count = 1
        else:
            count = 0
        if self.user.user.has_disciples:
            sum_count = Participation.objects.filter(user__user__master=self.user.user,
                                                     event=self.event,
                                                     user__user__disciples=None).aggregate(Sum('count'))
            sum_value = Participation.objects.filter(user__user__master=self.user.user,
                                                     event=self.event,
                                                     user__user__disciples=None).aggregate(Sum('value'))
            if sum_count.values()[0]:
                count += sum_count.values()[0]
            if sum_value.values()[0]:
                value += sum_value.values()[0]
        self.count_as_leader = count
        self.value_as_leader = value
        self.save()
        return self.count_as_leader


    def recount(self):
        from report.models import WeekReport
        self.get_count()
        self.get_as_leader_count()
        week = self.event.week
        user = self.user.user
        week_report = WeekReport.objects.get(user__user=user, week=week)
        week_report.get_home()
        week_report.get_night()
        week_report.get_service()
        if self.user.user.master:
            master_participation = Participation.objects.filter(user__user=self.user.user.master, event=self.event).first()
            if master_participation:
                master_participation.recount()
        return self


    @property
    def fields(self):
        l = self.user.user.fields
        d = OrderedDict()
        d['value'] = self.check
        l[u'check'] = d

        d = OrderedDict()
        d['value'] = self.value
        l[u'value'] = d

        d = OrderedDict()
        d['value'] = self.count
        l[u'count'] = d

        d = OrderedDict()
        d['value'] = self.count_as_leader
        l[u'count_as_leader'] = d

        return l

@receiver(signals.post_save, sender=Event)
def sync_event(sender, instance, **kwargs):
    if not instance.participations.all():
        users = EventAnket.objects.all()
        for user in users:
            participation = Participation.objects.create(event=instance, user=user, value=0)
            participation.save()


@receiver(signals.post_save, sender=Week)
def sync_week(sender, instance, **kwargs):
    from report.models import UserReport, WeekReport
    from create import create_events
    from utils import create_week_reports
    create_events(instance)
    from_date = instance.from_date
    to_date = instance.to_date
    create_week_reports(instance.id)


@receiver(signals.post_save, sender=Participation)
def sync_participation(sender, instance, **kwargs):
    from report.models import WeekReport
    week = instance.event.week
    user = instance.user.user
    try:
        week_report = WeekReport.objects.get(week=week, user__user=user)
        #week_report.get_home()
    except WeekReport.DoesNotExist:
        pass
