# -*- coding: utf-8
from __future__ import unicode_literals

import datetime
from collections import OrderedDict
from datetime import date

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

DAY_OF_THE_WEEK = {
    '1': _('Monday'),
    '2': _('Tuesday'),
    '3': _('Wednesday'),
    '4': _('Thursday'),
    '5': _('Friday'),
    '6': _('Saturday'),
    '7': _('Sunday'),
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
                  'Страна': 'user__country',
                  'Город': 'user__city',
                  'Примечание': 'description',
                  'Явка': 'check'}


def current_week():
    return datetime.date.today().isocalendar()[1]


@python_2_unicode_compatible
class EventType(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/eventTypes/', blank=True)
    home = models.BooleanField(default=False)
    night = models.BooleanField(default=False)
    service = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def event_count(self):
        return self.events.count()

    @property
    def last_event_date(self):
        last_event = self.events.last()
        return str(last_event.from_date)


@python_2_unicode_compatible
class EventAnket(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='event_anket', )

    def __str__(self):
        return self.user.get_full_name()


@python_2_unicode_compatible
class Week(models.Model):
    week = models.IntegerField(default=current_week, unique=True)
    from_date = models.DateField(default=date.today)
    to_date = models.DateField(default=date.today)

    def __str__(self):
        return str(self.week)


@python_2_unicode_compatible
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

    def __str__(self):
        return self.event_type.title

    @property
    def title(self):
        return self.event_type.title


@python_2_unicode_compatible
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

    def __str__(self):
        return '{} {}'.format(self.user, self.event)

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
            sum_count = Participation.objects.filter(user__user__master=self.user.user, event=self.event).aggregate(
                Sum('count'))
            sum_value = Participation.objects.filter(user__user__master=self.user.user, event=self.event).aggregate(
                Sum('value'))
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
            master_participation = Participation.objects.filter(user__user=self.user.user.master,
                                                                event=self.event).first()
            if master_participation:
                master_participation.recount()
        return self


@receiver(signals.post_save, sender=Event)
def sync_event(sender, instance, **kwargs):
    if not instance.participations.all():
        users = EventAnket.objects.all()
        for user in users:
            participation = Participation.objects.create(event=instance, user=user, value=0)
            participation.save()


@receiver(signals.post_save, sender=Week)
def sync_week(sender, instance, **kwargs):
    from .create import create_events
    from .utils import create_week_reports
    create_events(instance)
    create_week_reports(instance)


@receiver(signals.post_save, sender=Participation)
def sync_participation(sender, instance, **kwargs):
    pass
    # from report.models import WeekReport
    # week = instance.event.week
    # user = instance.user.user
    # try:
    #     WeekReport.objects.get(week=week, user__user=user)
    #     # week_report.get_home()
    # except WeekReport.DoesNotExist:
    #     pass


@python_2_unicode_compatible
class MeetingType(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    code = models.SlugField(_('Code'), max_length=255, unique=True)
    image = models.ImageField(_('Image'), upload_to='images/meeting_type/', blank=True)

    class Meta:
        verbose_name = _('Meeting type')
        verbose_name_plural = _('Meeting types')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('meeting_type:detail', kwargs={'code': self.code})


@python_2_unicode_compatible
class Meeting(models.Model):
    type = models.ForeignKey(MeetingType, on_delete=models.PROTECT, verbose_name=_('Meeting type'))
    date = models.DateField(_('Date'))

    owner = models.ForeignKey('account.CustomUser', limit_choices_to={'hierarchy__level': 1})
    visitors = models.ManyToManyField('account.CustomUser', through='event.MeetingAttend',
                                      related_name='meeting_types', verbose_name=_('Visitors'))
    total_sum = models.DecimalField(_('Total sum'), max_digits=12, decimal_places=0, default=0)

    class Meta:
        ordering = ('owner', '-date')
        verbose_name = _('Meeting')
        verbose_name_plural = _('Meetings')

    def __str__(self):
        return '{}: {}'.format(self.type.name, self.date.strftime('%d %B %Y'))


@python_2_unicode_compatible
class MeetingAttend(models.Model):
    user = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT,
                             related_name='attends', verbose_name=_('User'))
    meeting = models.ForeignKey('event.Meeting', on_delete=models.PROTECT,
                                related_name='attends', verbose_name=_('Meeting'))

    attended = models.BooleanField(_('Attended'), default=False)

    note = models.TextField(_('Note'), blank=True)

    class Meta:
        ordering = ('meeting__owner', '-meeting__date')
        verbose_name = _('Meeting attend')
        verbose_name_plural = _('Meeting attendees')

    def __str__(self):
        return '[{}] {} — visitor of {}'.format(
            'X' if self.attended else ' ',
            self.user,
            self.meeting)
