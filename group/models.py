# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import date

from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from account.abstact_models import UserPermission
from group.permissions import can_see_churches, can_see_home_groups


class GroupUserPermission(UserPermission):
    class Meta:
        abstract = True

    def can_see_churches(self):
        """
        Checking that the ``self`` user has the right to see list of churches
        """
        request = self._perm_req()
        return can_see_churches(request)

    def can_see_home_groups(self):
        """
        Checking that the ``self`` user has the right to see list of home groups
        """
        request = self._perm_req()
        return can_see_home_groups(request)


@python_2_unicode_compatible
class CommonGroup(models.Model):
    title = models.CharField(_('Title'), max_length=50, blank=True)
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
        return '{} {}'.format(self.city, self.owner_name)


class Church(CommonGroup):
    department = models.ForeignKey('hierarchy.Department', related_name='churches', on_delete=models.PROTECT,
                                   verbose_name=_('Department'))
    pastor = models.ForeignKey('account.CustomUser', related_name='church', on_delete=models.PROTECT,
                               verbose_name=_('Pastor'))
    country = models.CharField(_('Country'), max_length=50)
    is_open = models.BooleanField(default=False)
    users = models.ManyToManyField('account.CustomUser', related_name='churches', blank=True,
                                   verbose_name=_('Users'))

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
    leader = models.ForeignKey('account.CustomUser', related_name='home_group', on_delete=models.PROTECT,
                               verbose_name=_('Leader'))
    church = models.ForeignKey('Church', related_name='home_group', on_delete=models.CASCADE,
                               verbose_name=_('Church'))
    users = models.ManyToManyField('account.CustomUser', related_name='home_groups', blank=True,
                                   verbose_name=_('Users'))

    class Meta:
        verbose_name = _('Home Group')
        verbose_name_plural = _('Home Groups')
        ordering = ['-opening_date', '-id']

    def get_absolute_url(self):
        return reverse('home_group_detail', args=(self.id,))

    @property
    def owner_name(self):
        return self.leader.last_name
