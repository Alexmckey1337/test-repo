# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import date, datetime

from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from apps.analytics.models import LogModel
from apps.group.managers import ChurchManager, HomeGroupManager
from apps.event.models import Meeting, MeetingType, ChurchReport
from django.db import transaction
from apps.payment.models import get_default_currency
from apps.account.models import User
from django.db.models import Q


@python_2_unicode_compatible
class CommonGroup(models.Model):
    title = models.CharField(_('Title'), max_length=50)
    opening_date = models.DateField(_('Opening Date'), default=date.today)
    city = models.CharField(_('City'), max_length=50)
    address = models.CharField(_('Address'), max_length=300, blank=True)
    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
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


class Church(LogModel, CommonGroup):
    locality = models.ForeignKey('location.City', on_delete=models.SET_NULL, related_name='churches',
                                 null=True, blank=True, verbose_name=_('Locality'),
                                 help_text=_('City/village/etc'))
    department = models.ForeignKey('hierarchy.Department', related_name='churches',
                                   on_delete=models.PROTECT, verbose_name=_('Department'))
    pastor = models.ForeignKey('account.CustomUser', related_name='church',
                               on_delete=models.PROTECT, verbose_name=_('Pastor'))
    country = models.CharField(_('Country'), max_length=50)
    is_open = models.BooleanField(default=False)
    report_currency = models.IntegerField(default=get_default_currency, verbose_name=_('Report Currency'))

    image = models.ImageField(_('Church Image'), upload_to='churches/', blank=True, null=True)

    region = models.CharField(_('Region'), max_length=50, blank=True, null=True)

    objects = ChurchManager()

    tracking_fields = (
        'title', 'opening_date', 'city', 'address', 'phone_number', 'website',
        'department', 'pastor', 'country',
        'is_open', 'report_currency', 'image', 'region', 'locality',
    )

    tracking_reverse_fields = ()

    def save(self, *args, **kwargs):
        is_create = True if not self.pk else False
        super(Church, self).save(*args, **kwargs)

        if is_create:
            ChurchReport.objects.create(church=self,
                                        pastor=self.pastor,
                                        date=datetime.now().date(),
                                        currency_id=self.report_currency)

    class Meta:
        verbose_name = _('Church')
        verbose_name_plural = _('Churches')
        ordering = ['-opening_date', '-id']

    def get_absolute_url(self):
        return reverse('church_detail', args=(self.id,))

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def owner_name(self):
        return self.pastor.last_name

    @property
    def stable_count(self):
        return User.objects.filter(Q(customuser__cchurch=self, customuser__is_stable=True) | Q(
            customuser__hhome_group__church=self, customuser__is_stable=True)).count()

    @property
    def count_people(self):
        return User.objects.filter(Q(customuser__cchurch=self) | Q(
            customuser__hhome_group__church=self)).count()

    @property
    def count_home_groups(self):
        return User.objects.filter(customuser__church=self).count()


class HomeGroup(LogModel, CommonGroup):
    locality = models.ForeignKey('location.City', on_delete=models.SET_NULL, related_name='home_groups',
                                 null=True, blank=True, verbose_name=_('Locality'),
                                 help_text=_('City/village/etc'))
    leader = models.ForeignKey('account.CustomUser', related_name='home_group',
                               on_delete=models.PROTECT, verbose_name=_('Leader'))
    church = models.ForeignKey('Church', related_name='home_group',
                               on_delete=models.PROTECT, verbose_name=_('Church'))
    active = models.BooleanField(default=True)

    image = models.ImageField(_('Home Group Image'), upload_to='home_groups/', blank=True, null=True)

    objects = HomeGroupManager()

    tracking_fields = (
        'title', 'opening_date', 'city', 'address', 'phone_number', 'website',
        'leader', 'church', 'active', 'image', 'locality',
    )

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
