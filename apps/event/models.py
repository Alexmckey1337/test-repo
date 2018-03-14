# -*- coding: utf-8
from __future__ import unicode_literals

import datetime

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _

from apps.analytics.decorators import log_change_payment
from apps.event.managers import MeetingManager, ChurchReportManager
from apps.navigation.table_columns import get_table
from apps.payment.models import AbstractPaymentPurpose, get_default_currency
from common import date_utils


@python_2_unicode_compatible
class MeetingType(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    code = models.SlugField(_('Code'), max_length=255, unique=True)
    image = models.ImageField(_('Image'), upload_to='images', blank=True)

    class Meta:
        verbose_name = _('Meeting type')
        verbose_name_plural = _('Meeting types')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class MeetingAttend(models.Model):
    user = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT, related_name='attends',
                             verbose_name=_('User'))

    meeting = models.ForeignKey('event.Meeting', on_delete=models.CASCADE, related_name='attends',
                                verbose_name=_('Meeting'))

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

    @property
    def phone_number(self):
        return self.user.phone_number


@python_2_unicode_compatible
class AbstractStatusModel(models.Model):
    IN_PROGRESS, SUBMITTED, EXPIRED = 1, 2, 3

    STATUS_LIST = (
        (IN_PROGRESS, _('in_progress')),
        (SUBMITTED, _('submitted')),
        (EXPIRED, _('expired')),
    )
    status = models.PositiveSmallIntegerField(_('Status'), choices=STATUS_LIST, default=IN_PROGRESS)

    class Meta:
        abstract = True


def get_event_week():
    week = timezone.now().isocalendar()[1]
    return 'event/%s/' % week


@python_2_unicode_compatible
class Meeting(AbstractStatusModel):
    date = models.DateField(_('Date'))
    type = models.ForeignKey(MeetingType, on_delete=models.PROTECT, verbose_name=_('Meeting type'))

    owner = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT,
                              limit_choices_to={'hierarchy__level__gte': 1})

    home_group = models.ForeignKey('group.HomeGroup', on_delete=models.CASCADE,
                                   verbose_name=_('Home Group'))

    visitors = models.ManyToManyField('account.CustomUser', verbose_name=_('Visitors'),
                                      through='event.MeetingAttend',
                                      related_name='meeting_types')

    total_sum = models.DecimalField(_('Total sum'), max_digits=12,
                                    decimal_places=2, default=0)

    image = models.ImageField(_('Event Image'), upload_to=get_event_week(), blank=True, null=True)

    objects = MeetingManager()

    class Meta:
        ordering = ('-id', '-date')
        verbose_name = _('Meeting')
        verbose_name_plural = _('Meetings')
        unique_together = ['type', 'date', 'home_group']

    def __str__(self):
        return 'Отчет ДГ - {} ({}): {}'.format(
            self.home_group,
            self.type.name,
            self.date.strftime('%d %B %Y'))

    def get_absolute_url(self):
        return reverse('events:meeting_report_detail', args=(self.id,))

    @property
    def phone_number(self):
        return self.home_group.phone_number

    @property
    def church(self):
        return self.home_group.church

    @property
    def department(self):
        return self.home_group.church.department

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def table_columns(self):
        return get_table('meeting', self.request.user.id)

    @cached_property
    def can_submit(self):
        # if Meeting.objects.filter(owner=self.owner, status=Meeting.EXPIRED).exists() \
        #         and self.status == Meeting.IN_PROGRESS:
        #     return False
        return True

    @property
    def cant_submit_cause(self):
        if not self.can_submit:
            return _('Невозможно подать отчет. Данный лидер имеет просроченные отчеты.')
        return ''


@python_2_unicode_compatible
class ChurchReport(AbstractStatusModel, AbstractPaymentPurpose):
    pastor = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT,
                               limit_choices_to={'hierarchy__level__gte': 2})
    church = models.ForeignKey('group.Church', on_delete=models.CASCADE,
                               verbose_name=_('Church'))
    date = models.DateField(_('Date'))
    count_people = models.IntegerField(_('Count People'), default=0)
    new_people = models.IntegerField(_('New People'), default=0)
    count_repentance = models.IntegerField(_('Number of Repentance'), default=0)
    tithe = models.DecimalField(_('Tithe'), max_digits=12, decimal_places=2, default=0)
    donations = models.DecimalField(_('Donations'), max_digits=12,
                                    decimal_places=2, default=0)
    currency_donations = models.CharField(_('Donations in Currency'),
                                          max_length=150, blank=True)
    comment = models.TextField(_('Comment'), blank=True)

    transfer_payments = models.DecimalField(_('Transfer Payments'), max_digits=12,
                                            decimal_places=2, default=0, blank=True)
    pastor_tithe = models.DecimalField(_('Pastor Tithe'), max_digits=12,
                                       decimal_places=2, default=0)

    payments = GenericRelation('payment.Payment', related_query_name='church_reports',
                               on_delete=models.PROTECT)
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency'),
                                 default=get_default_currency, null=True)
    done = models.BooleanField(default=False)

    objects = ChurchReportManager()

    class Meta:
        ordering = ('-id', '-date')
        verbose_name = _('Church Report')
        verbose_name_plural = _('Church Reports')
        unique_together = ['church', 'date', 'status']

    def __str__(self):
        return 'Отчет Церкви - {}: {}'.format(
            self.church.get_title,
            self.date.strftime('%d %B %Y'))

    def get_absolute_url(self):
        return reverse('events:church_report_detail', args=(self.id,))

    @log_change_payment(['done'])
    def update_after_cancel_payment(self, editor, payment):
        self.done = False
        self.save()

    update_after_cancel_payment.alters_data = True

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def department(self):
        return self.church.department

    @cached_property
    def can_submit(self):
        if ChurchReport.objects.filter(pastor=self.pastor, status=ChurchReport.EXPIRED).exists() \
                and self.status == ChurchReport.IN_PROGRESS:
            return False
        return True

    @property
    def cant_submit_cause(self):
        if not self.can_submit:
            return _('Невозможно подать отчет. Данный пастор имеет просроченные отчеты.')
        return ''


"""
#######################################################################################################
#######################################################################################################
"""


def current_week():
    return timezone.now().isocalendar()[1]


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
    user = models.OneToOneField('account.CustomUser', on_delete=models.PROTECT, related_name='event_anket', )

    def __str__(self):
        return self.user.get_full_name()


@python_2_unicode_compatible
class Week(models.Model):
    week = models.IntegerField(default=current_week, unique=True)
    from_date = models.DateField(default=date_utils.today)
    to_date = models.DateField(default=date_utils.today)

    def __str__(self):
        return str(self.week)


@python_2_unicode_compatible
class Event(models.Model):
    week = models.ForeignKey(Week, on_delete=models.PROTECT, null=True, blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT,
                                   related_name='events', blank=True, null=True)
    from_date = models.DateField(default=date_utils.today)
    to_date = models.DateField(default=date_utils.today)
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
    user = models.ForeignKey(EventAnket, on_delete=models.PROTECT, related_name='participations')
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='participations')
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
        from apps.report.models import WeekReport
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
