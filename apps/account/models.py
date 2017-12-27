# -*- coding: utf-8
from __future__ import unicode_literals

import binascii
import os
from collections import OrderedDict

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from treebeard.mp_tree import MP_Node

from apps.account.abstract_models import CustomUserAbstract
from apps.account.api.permissions import (
    can_edit_status_block, can_edit_description_block, can_see_account_page,
    SeeUserListPermission, CreateUserPermission, ExportUserListPermission)
from apps.account.managers import CustomUserManager
from apps.analytics.models import LogModel
from apps.group.abstract_models import GroupUserPermission
from apps.navigation.models import Table
from apps.partnership.abstract_models import PartnerUserPermission
from apps.partnership.api.permissions import can_edit_partner_block, can_see_partner_block, can_see_deal_block
from apps.summit.abstract_models import SummitUserPermission
from apps.summit.models import SummitAnket, Summit


@python_2_unicode_compatible
class CustomUser(MP_Node, LogModel, User, CustomUserAbstract,
                 GroupUserPermission, PartnerUserPermission, SummitUserPermission):
    """
    User model
    """
    steplen = 6

    region = models.CharField(_('Region'), max_length=50, blank=True)
    district = models.CharField(_('District'), max_length=50, blank=True)
    address = models.CharField(_('Address'), max_length=300, blank=True)

    phone_number = models.CharField(_('Phone number'), max_length=23, blank=True, db_index=True)
    skype = models.CharField(_('Skype'), max_length=50, blank=True)
    facebook = models.URLField(_('Facebook URL'), default='', blank=True, null=True)
    vkontakte = models.URLField(_('Vkontakte URL'), default='', blank=True, null=True)
    odnoklassniki = models.URLField(_('Odnoklassniki URL'), default='', blank=True, null=True)

    image = models.ImageField(_('Image'), upload_to='images/', blank=True)
    image_source = models.ImageField(_('Source of image'), upload_to='images/', blank=True)
    description = models.TextField(_('Description'), blank=True)
    #: Born date
    born_date = models.DateField(_('Born date'), blank=True, null=True, db_index=True)
    #: Date of repentance (дата покаяния)
    repentance_date = models.DateField(_('Repentance date'), blank=True, null=True)
    #: Date of coming (дата прихода)
    coming_date = models.DateField(_('Coming date'), blank=True, null=True)
    activation_key = models.CharField(_('Activation key'), max_length=40, blank=True)

    departments = models.ManyToManyField('hierarchy.Department', related_name='users', verbose_name=_('Departments'))
    hierarchy = models.ForeignKey('hierarchy.Hierarchy', related_name='users', null=True, blank=True,
                                  on_delete=models.SET_NULL, verbose_name=_('Hierarchy'), db_index=True)
    master = models.ForeignKey('self', related_name='disciples', null=True, blank=True, verbose_name=_('Master'),
                               on_delete=models.PROTECT, db_index=True)
    managers = models.ManyToManyField('self', related_name='skins', blank=True, verbose_name=_('Manager'),
                                      symmetrical=False)

    extra_phone_numbers = ArrayField(
        models.CharField(_('Number'), max_length=255),
        verbose_name=_('Extra Phone Numbers'),
        blank=True, null=True,
    )

    can_login = models.BooleanField(_('Can login to site'), default=False)

    cchurch = models.ForeignKey('group.Church', on_delete=models.SET_NULL,
                                related_name='uusers', verbose_name=_('Church'),
                                null=True, blank=True, db_index=True)

    hhome_group = models.ForeignKey('group.HomeGroup', on_delete=models.SET_NULL,
                                    related_name='uusers', verbose_name=_('Home group'),
                                    null=True, blank=True, db_index=True)

    marker = models.ManyToManyField('UserMarker', related_name='users',
                                    verbose_name=_('User Marker'), blank=True)

    objects = CustomUserManager()

    tracking_fields = (
        'first_name', 'last_name', 'middle_name', 'search_name', 'email', 'phone_number', 'skype', 'image',
        'country', 'region', 'city', 'district', 'address', 'born_name', 'facebook', 'vkontakte',
        'odnoklassniki', 'description', 'hierarchy', 'master', 'repentance_date',
        'coming_date', 'spiritual_level', 'extra_phone_numbers', 'cchurch', 'hhome_group',
    )

    tracking_reverse_fields = (
        'divisions', 'departments'
    )

    def __str__(self):
        return self.fullname

    class Meta:
        ordering = ['-date_joined']

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        for profile in self.summit_profiles.all():
            profile.save()
        SummitAnket.objects.filter(
            summit__status=Summit.OPEN,
            user_id__in=self.disciples.values_list('pk', flat=True)).update(responsible=self.fullname)

    # TODO hack
    def regcode(self):
        profile = self.summit_profiles.filter(summit_id=7).first()
        if profile:
            return profile.reg_code
        return ''

    def get_absolute_url(self):
        return reverse('account:detail', args=(self.id,))

    def get_descendant_leaders(self):
        return self.get_descendants().filter(hierarchy__level=1)

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def get_church(self):
        return self.cchurch or self.hhome_group.church if self.hhome_group else None

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
        return self.master.short

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

    def get_pastor(self):
        master = self.master
        while master is not None:
            if master.hierarchy and master.hierarchy.level == 2:
                return master
            master = master.master
        return None

    def get_bishop(self):
        master = self.master
        while master is not None:
            if master.hierarchy and master.hierarchy.level == 4:
                return master
            master = master.master
        return None

    def get_sotnik(self):
        return self.get_pastor()

    @property
    def fullname(self):
        return ' '.join(map(lambda name: name.strip(), (self.last_name, self.first_name, self.middle_name)))

    @property
    def is_guest(self):
        return self.hierarchy is None or self.hierarchy.level == 0

    @property
    def is_congregation(self):
        return self.hierarchy is not None and self.hierarchy.level == 0

    @property
    def is_leader(self):
        return self.hierarchy is not None and self.hierarchy.level == 1

    @property
    def is_leader_or_high(self):
        return self.hierarchy is not None and self.hierarchy.level >= 1

    @property
    def is_pastor(self):
        return self.hierarchy is not None and self.hierarchy.level == 2

    @property
    def is_pastor_or_high(self):
        return self.hierarchy is not None and self.hierarchy.level >= 2

    @property
    def is_sotnik(self):
        return self.is_pastor

    @property
    def is_sotnik_or_high(self):
        return self.is_pastor_or_high

    @property
    def is_bishop(self):
        return self.hierarchy is not None and self.hierarchy.level == 4

    @property
    def is_bishop_or_high(self):
        return self.hierarchy is not None and self.hierarchy.level >= 4

    @property
    def is_main_bishop(self):
        return self.hierarchy is not None and self.hierarchy.level == 5

    @property
    def is_main_bishop_or_high(self):
        return self.hierarchy is not None and self.hierarchy.level >= 5

    @property
    def is_senior_bishop(self):
        return self.hierarchy is not None and self.hierarchy.level == 60

    @property
    def is_senior_bishop_or_high(self):
        return self.hierarchy is not None and self.hierarchy.level >= 60

    @property
    def is_apostle(self):
        return self.hierarchy is not None and self.hierarchy.level == 70

    @property
    def is_apostle_or_high(self):
        return self.hierarchy is not None and self.hierarchy.level >= 70

    @property
    def is_archon(self):
        return self.hierarchy is not None and self.hierarchy.level == 80

    @property
    def is_archon_or_high(self):
        return self.hierarchy is not None and self.hierarchy.level >= 80

    # PERMISSIONS

    def can_see_account_page(self, user):
        """
        Checking that the ``self`` user has the right to see page ``/account/<user.id>/``
        """
        return can_see_account_page(self, user)

    def can_create_user(self):
        """
        Checking that the ``self`` user has the right to create a new user
        """
        return CreateUserPermission(self).has_permission()

    def can_export_user_list(self):
        """
        Checking that the ``self`` user has the right to export list of users
        """
        return ExportUserListPermission(self).has_permission()

    def can_see_user_list(self):
        """
        Checking that the ``self`` user has the right to see list of users
        """
        return SeeUserListPermission(self).has_permission()

    # Account page: /account/<user_id>/

    def can_edit_status_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to edit fields of ``user``:

        - department
        - status
        - master
        - divisions
        """
        return can_edit_status_block(self, user)

    def can_edit_description_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to edit fields of ``user``:

        - description
        """
        return can_edit_description_block(self, user)

    def can_edit_partner_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to edit fields of ``user``:

        - partnership.is_active
        - partnership.date
        - partnership.value and partnership.currency
        - partnership.responsible
        """
        return can_edit_partner_block(self, user)

    def can_see_partner_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to see partner block of ``user``
        """
        return can_see_partner_block(self, user)

    def can_see_deal_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to see deals block of ``user``
        """
        return can_see_deal_block(self, user)


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
    if instance.can_login:
        Table.objects.get_or_create(user=instance)


class UserMarker(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    color = models.CharField(_('Color'), max_length=255)
    description = models.TextField(_('Description'))

    class Meta:
        verbose_name = _('User Marker')
        verbose_name_plural = _('User Markers')

    def __str__(self):
        return "User's marker - %s." % self.title
