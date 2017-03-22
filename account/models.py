# -*- coding: utf-8
from __future__ import unicode_literals

import binascii
import os
from collections import OrderedDict

from django.contrib.auth.models import User, UserManager
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey

from account.permissions import can_see_churches, can_see_home_groups
from event.models import EventAnket
from navigation.models import Table
from partnership.models import Partnership
from partnership.permissions import can_see_partners, can_see_partner_stats, can_see_deals
from summit.models import SummitType, SummitAnket
from summit.permissions import can_see_summit, can_see_summit_type, can_see_any_summit, can_see_any_summit_type


class CustomUserManager(TreeManager, UserManager):
    use_in_migrations = False


@python_2_unicode_compatible
class CustomUser(MPTTModel, User):
    middle_name = models.CharField(max_length=40, blank=True)

    #: Field for name in the native language of the user
    search_name = models.CharField(_('Field for search by name'), max_length=255, blank=True)

    phone_number = models.CharField(max_length=23, blank=True)
    skype = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=300, blank=True)
    born_date = models.DateField(blank=True, null=True)
    facebook = models.URLField(default='', blank=True, null=True)
    vkontakte = models.URLField(default='', blank=True, null=True)
    odnoklassniki = models.URLField(default='', blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True)
    image_source = models.ImageField(upload_to='images/', blank=True)
    description = models.TextField(blank=True)
    departments = models.ManyToManyField('hierarchy.Department', related_name='users')
    hierarchy = models.ForeignKey('hierarchy.Hierarchy', related_name='users', null=True, blank=True,
                                  on_delete=models.SET_NULL)
    master = TreeForeignKey('self', related_name='disciples', null=True, blank=True,
                            on_delete=models.PROTECT, db_index=True)
    repentance_date = models.DateField(blank=True, null=True)
    coming_date = models.DateField(blank=True, null=True)
    hierarchy_order = models.BigIntegerField(blank=True, null=True)
    activation_key = models.CharField(max_length=40, blank=True)

    extra_phone_numbers = ArrayField(
        models.CharField(_('Number'), max_length=255),
        verbose_name=_('Extra Phone Numbers'),
        blank=True, null=True,
    )

    BABY, JUNIOR, FATHER = 1, 2, 3
    SPIRITUAL_LEVEL_CHOICES = (
        (BABY, _('Baby')),
        (JUNIOR, _('Junior')),
        (FATHER, _('Father')),
    )
    spiritual_level = models.PositiveSmallIntegerField(_('Spiritual Level'), choices=SPIRITUAL_LEVEL_CHOICES, default=1)

    objects = CustomUserManager()

    def __str__(self):
        return self.fullname

    class Meta:
        ordering = ['-date_joined']

    class MPTTMeta:
        parent_attr = 'master'

    def get_absolute_url(self):
        return reverse('account:detail', args=(self.id,))

    def get_descendant_leaders(self):
        return self.get_descendants().filter(hierarchy__level=1)

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def is_partner_manager(self):
        return self.partnership and self.partnership.level == Partnership.MANAGER

    @property
    def is_partner_manager_or_high(self):
        return self.partnership and self.partnership.level <= Partnership.MANAGER

    @property
    def is_partner_supervisor(self):
        return self.partnership and self.partnership.level == Partnership.SUPERVISOR

    @property
    def is_partner_supervisor_or_high(self):
        return self.partnership and self.partnership.level <= Partnership.SUPERVISOR

    @property
    def is_partner_director(self):
        return self.partnership and self.partnership.level == Partnership.DIRECTOR

    def available_summit_types(self):
        return SummitType.objects.filter(summits__ankets__user=self,
                                         summits__ankets__role__gte=SummitAnket.CONSULTANT).distinct()

    @property
    def column_table(self):
        l = OrderedDict()
        if hasattr(self, 'table') and isinstance(self.table, Table):
            columns = self.table.columns.order_by('number')
            for column in columns.all():
                d = OrderedDict()
                d['id'] = column.id
                d['title'] = column.columnType.verbose_title
                d['ordering_title'] = column.columnType.ordering_title
                d['number'] = column.number
                d['active'] = column.active
                d['editable'] = column.editable
                l[column.columnType.title] = d
        return l

    @property
    def master_short_fullname(self):
        s = ''
        if self.master:
            if len(self.master.last_name) > 0:
                s = s + self.master.last_name + ' '
            if len(self.master.first_name) > 0:
                s = s + self.master.first_name[0] + '.'
            if len(self.master.middle_name) > 0:
                s = s + self.master.middle_name[0] + '.'
        return s

    @property
    def short(self):
        s = ''
        if len(self.last_name) > 0:
            s = s + self.last_name + ' '
        if len(self.first_name) > 0:
            s = s + self.first_name[0] + '.'
        if len(self.middle_name) > 0:
            s = s + self.middle_name[0] + '.'
        return s

    @property
    def fullname(self):
        return ' '.join(map(lambda name: name.strip(), (self.last_name, self.first_name, self.middle_name)))

    # PERMISSIONS

    def _perm_req(self):
        return type('Request', (), {'user': self})

    # database block

    def can_see_churches(self):
        request = self._perm_req()
        return can_see_churches(request)

    def can_see_home_groups(self):
        request = self._perm_req()
        return can_see_home_groups(request)

    # partner block

    def can_see_partners(self):
        request = self._perm_req()
        return can_see_partners(request)

    def can_see_deals(self):
        request = self._perm_req()
        return can_see_deals(request)

    def can_see_partner_stats(self):
        request = self._perm_req()
        return can_see_partner_stats(request)

    def can_see_any_partner_block(self):
        return any((self.can_see_partners(), self.can_see_deals(), self.can_see_partner_stats()))

    # summit block

    def can_see_summit(self, summit_id):
        request = self._perm_req()
        return can_see_summit(request, summit_id)

    def can_see_summit_type(self, summit_type):
        request = self._perm_req()
        return can_see_summit_type(request, summit_type)

    def can_see_any_summit(self):
        request = self._perm_req()
        return can_see_any_summit(request)

    def can_see_any_summit_type(self):
        request = self._perm_req()
        return can_see_any_summit_type(request)


@python_2_unicode_compatible
class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.ForeignKey(
        'account.CustomUser', related_name='auth_tokens',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


def create_custom_user(sender, instance, created, **kwargs):
    if created:
        values = {}
        for field in sender._meta.local_fields:
            values[field.attname] = getattr(instance, field.attname)
        user = CustomUser(**values)
        user.save()


post_save.connect(create_custom_user, User)


@receiver(signals.post_save, sender=CustomUser)
def sync_user(sender, instance, **kwargs):
    from notification.models import Notification, NotificationTheme
    birth_day_notification_theme = NotificationTheme.objects.filter(birth_day=True).first()
    if instance.born_date:
        date = instance.born_date
        try:
            Notification.objects.filter(theme__birth_day=True, user=instance).update(date=date)
        except Notification.DoesNotExist:
            # description = "Сегодня свой день рождения отмечает %s." % instance.fullname
            Notification.objects.create(date=date,
                                        user=instance,
                                        theme=birth_day_notification_theme)
    Table.objects.get_or_create(user=instance)
