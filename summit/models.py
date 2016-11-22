# -*- coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class SummitType(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название саммита')
    club_name = models.CharField(_('Club name'), max_length=30, blank=True)
    image = models.ImageField(upload_to='summit_type/images/', blank=True)

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''


@python_2_unicode_compatible
class Summit(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.ForeignKey('SummitType', related_name='summits', blank=True, null=True)
    description = models.CharField(max_length=255, verbose_name='Описание',
                                   blank=True, null=True)

    class Meta:
        ordering = ('type',)
        verbose_name = _('Summit')
        verbose_name_plural = _('Summits')

    def __str__(self):
        return '%s %s' % (self.type.title, self.start_date)

    @property
    def consultants(self):
        return self.ankets.filter(role__gte=SummitAnket.CONSULTANT)

    @property
    def title(self):
        return self.type.title

    @property
    def club_name(self):
        return self.type.club_name


@python_2_unicode_compatible
class SummitAnket(models.Model):
    user = models.ForeignKey('account.CustomUser', related_name='summit_ankets')
    summit = models.ForeignKey('Summit', related_name='ankets', verbose_name='Саммит',
                               blank=True, null=True)

    value = models.PositiveSmallIntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=8, blank=True)
    name = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    pastor = models.CharField(max_length=255, blank=True)
    bishop = models.CharField(max_length=255, blank=True)
    sotnik = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=date.today)
    department = models.CharField(max_length=255, blank=True)
    protected = models.BooleanField(default=False)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=255, blank=True)
    responsible = models.CharField(max_length=255, blank=True)
    image = models.CharField(max_length=12, blank=True)
    retards = models.BooleanField(default=False)

    visited = models.BooleanField(default=False)

    VISITOR, CONSULTANT, SUPERVISOR = 10, 20, 30
    ROLES = (
        (VISITOR, _('Visitor')),
        (CONSULTANT, _('Consultant')),
        (SUPERVISOR, _('Supervisor')),
    )
    role = models.PositiveSmallIntegerField(_('Summit Role'), choices=ROLES, default=VISITOR)

    summit_consultants = models.ManyToManyField(
        'summit.Summit', related_name='consultant_ankets',
        through='summit.SummitUserConsultant', through_fields=('user', 'summit'))

    class Meta:
        unique_together = (('user', 'summit'),)

    def __str__(self):
        return '%s %s %s' % (self.user.fullname, self.summit.type.title, self.summit.start_date)

    @property
    def is_member(self):
        summit_type = self.summit.type
        return summit_type.summits.filter(ankets__visited=True, ankets__user=self.user).exists()

    @property
    def info(self):
        d = OrderedDict()
        d['value'] = '0'
        if self.value:
            d['value'] = self.value
        d['title'] = "Информация про оплату"
        d['verbose'] = 'money_info'
        d['summit_title'] = ''
        d['summit_type_id'] = self.summit.type.id
        d['summit_anket_id'] = self.id
        d['description'] = self.description
        if self.summit.title:
            d['summit_title'] = self.summit.title
        d['start_date'] = ''
        if self.summit.start_date:
            d['start_date'] = self.summit.start_date
        l = self.user.fields
        l['money_info'] = d
        d = OrderedDict()
        d['value'] = self.description
        d['verbose'] = 'description'
        l['description'] = d
        return l

    @property
    def common(self):
        l = OrderedDict([('Оплата', 'money_info'),
                         ('Примечание', 'description'),
                         ])
        return l


@python_2_unicode_compatible
class AnketEmail(models.Model):
    anket = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='emails',
                              verbose_name=_('Anket'))
    recipient = models.CharField(_('Email'), max_length=255)

    subject = models.CharField(_('Subject'), max_length=255, blank=True)
    text = models.TextField(_('Text'), blank=True)
    html = models.TextField(_('HTML text'), blank=True)
    attach = models.FileField(_('Attach'), upload_to='tickets', null=True, blank=True)

    created_at = models.DateTimeField(_('Date created'), auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.created_at, self.anket)

    class Meta:
        ordering = ('-created_at', 'anket')
        verbose_name = _('Anket email')
        verbose_name_plural = _('Anket emails')


@python_2_unicode_compatible
class SummitLesson(models.Model):
    summit = models.ForeignKey('summit.Summit', on_delete=models.CASCADE, related_name='lessons',
                               related_query_name='lessons', verbose_name=_('Summit'))
    viewers = models.ManyToManyField('summit.SummitAnket', related_name='all_lessons',
                                     verbose_name=_('Viewers'))
    name = models.CharField(_('Name'), max_length=255)

    def __str__(self):
        return '{}: {}'.format(self.summit, self.name)

    class Meta:
        ordering = ('summit', 'name')
        verbose_name = _('Summit lesson')
        verbose_name_plural = _('Summit lessons')
        unique_together = ('name', 'summit')


@python_2_unicode_compatible
class SummitUserConsultant(models.Model):
    consultant = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='consultees',
                                   limit_choices_to={'role__gte': SummitAnket.CONSULTANT},
                                   verbose_name=_('Consultant'))
    user = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='consultants',
                             verbose_name=_('User'))
    summit = models.ForeignKey('summit.Summit', on_delete=models.CASCADE, related_name='consultees',
                               verbose_name=_('Summit'))

    def __str__(self):
        return '{}: {} is consultant for {}'.format(self.summit, self.consultant, self.user)

    class Meta:
        verbose_name = _('Summit consultant')
        verbose_name_plural = _('Summit consultants')
        unique_together = ('user', 'summit')

    def clean(self):
        if self.summit != self.user.summit:
            raise ValidationError(_('Этот пользователь не участвует в данном саммите.'))
        if self.summit != self.consultant.summit:
            raise ValidationError(_('Этот пользователь не является консультантом на данном саммите.'))


@python_2_unicode_compatible
class SummitAnketNote(models.Model):
    summit_anket = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='notes',
                                     verbose_name=_('Summit anket'))
    owner = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, related_name='notes',
                              null=True, blank=True, verbose_name=_('Owner of note'))

    text = models.CharField(_('Note'), max_length=1000)

    date_created = models.DateTimeField(_('Datetime created'), auto_now_add=True)

    def __str__(self):
        return self.short_text

    @property
    def short_text(self):
        return '{}...'.format(self.text[:47]) if len(self.text) > 50 else self.text

    @property
    def owner_name(self):
        return self.owner.fullname

    class Meta:
        verbose_name = _('Summit Anket Note')
        verbose_name_plural = _('Summit Anket Notes')
        ordering = ('date_created',)
