# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import date, datetime

from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from group.managers import ChurchManager, HomeGroupManager
from event.models import Meeting, MeetingType
from django.db import transaction
from payment.models import get_default_currency


@python_2_unicode_compatible
class CommonGroup(models.Model):
    title = models.CharField(_('Title'), max_length=50)
    opening_date = models.DateField(_('Opening Date'), default=date.today)
    city = models.CharField(_('City'), max_length=50)
    address = models.CharField(_('Address'), max_length=300, blank=True)
    phone_number = models.CharField(_('Phone Number'), max_length=13, blank=True)
    website = models.URLField(_('Web Site'), blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.get_title

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def get_title(self):
        if self.title:
            return self.title
        return '{} {}'.format(self.owner_name, self.city)


class Church(CommonGroup):
    department = models.ForeignKey('hierarchy.Department', related_name='churches',
                                   on_delete=models.PROTECT, verbose_name=_('Department'))
    pastor = models.ForeignKey('account.CustomUser', related_name='church',
                               on_delete=models.PROTECT, verbose_name=_('Pastor'))
    country = models.CharField(_('Country'), max_length=50)
    is_open = models.BooleanField(default=False)
    report_currency = models.IntegerField(default=get_default_currency(), verbose_name=_('Report Currency'))

    objects = ChurchManager()

    class Meta:
        verbose_name = _('Church')
        verbose_name_plural = _('Churches')
        ordering = ['-opening_date', '-id']

    def get_absolute_url(self):
        return reverse('church_detail', args=(self.id,))

    @property
    def owner_name(self):
        return self.pastor.last_name


class HomeGroup(CommonGroup):
    leader = models.ForeignKey('account.CustomUser', related_name='home_group',
                               on_delete=models.PROTECT, verbose_name=_('Leader'))
    church = models.ForeignKey('Church', related_name='home_group',
                               on_delete=models.CASCADE, verbose_name=_('Church'))
    active = models.BooleanField(default=True)

    objects = HomeGroupManager()

    def save(self, *args, **kwargs):
        is_create = True if not self.pk else False
        super(HomeGroup, self).save(*args, **kwargs)

        if is_create:
            meeting_types = MeetingType.objects.all()
            with transaction.atomic():
                for meeting_type in meeting_types:
                    Meeting.objects.create(home_group=self,
                                           owner=self.leader,
                                           date=datetime.now().date(),
                                           type=meeting_type)

        if self.leader and self.pk:
            Meeting.objects.filter(home_group=self, status=Meeting.IN_PROGRESS).update(owner=self.leader)

    class Meta:
        verbose_name = _('Home Group')
        verbose_name_plural = _('Home Groups')
        ordering = ['-opening_date', '-id']

    def get_absolute_url(self):
        return reverse('home_group_detail', args=(self.id,))

    @property
    def owner_name(self):
        return self.leader.last_name
