# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models
from datetime import date
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _


class CommonGroup(models.Model):
    title = models.CharField(_('Title'), max_length=50, blank=True)
    opening_date = models.DateField(_('Opening Date'), default=date.today)
    city = models.CharField(_('City'), max_length=50)
    address = models.CharField(_('Address'), max_length=300, blank=True)
    phone_number = models.CharField(_('Phone Number'), max_length=13, blank=True)
    website = models.URLField(_('Web Site'), blank=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Church(CommonGroup):
    department = models.ForeignKey('hierarchy.Department', related_name='churches', on_delete=models.PROTECT,
                                   verbose_name=_('Department'))
    pastor = models.ForeignKey('account.CustomUser', related_name='church', on_delete=models.PROTECT,
                               verbose_name=_('Pastor'))
    is_open = models.BooleanField(default=False)
    users = models.ManyToManyField('account.CustomUser', related_name='churches', blank=True,
                                   verbose_name=_('Users'))

    class Meta:
        verbose_name = _('Church')
        verbose_name_plural = _('Churches')

    def __str__(self):
        return '{}'.format(self.title)

    def get_absolute_url(self):
        return '/churches/{}/'.format(self.id)

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def get_title(self):
        return '{} {}'.format(self.city, self.pastor.last_name)


@python_2_unicode_compatible
class HomeGroup(CommonGroup):
    leader = models.ForeignKey('account.CustomUser', related_name='home_group', on_delete=models.PROTECT,
                               verbose_name=_('Leader'))
    church = models.ForeignKey('Church', related_name='home_group', on_delete=models.CASCADE,
                               verbose_name=_('Church'))
    users = models.ManyToManyField('account.CustomUser', related_name='home_groups', blank=True,
                                   verbose_name=_('Users'))

    class Meta:
        verbose_name = _('Home Group')
        verbose_name_plural = _('Home Groups')

    def __str__(self):
        return '{}'.format(self.title)

    def get_absolute_url(self):
        return 'churches/{}/home_groups/{}/'.format(self.church_id, self.id)

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def get_title(self):
        return '{} {}'.format(self.city, self.leader.last_name)
