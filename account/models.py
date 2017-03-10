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

from event.models import EventAnket
from navigation.models import Table
from partnership.models import Partnership
from summit.models import SummitType, SummitAnket

COMMON = ['Имя', 'Фамилия', 'Отчество', 'Email', 'Телефон', 'Дата рождения', 'Иерархия', 'Отдел',
          'Страна', 'Область', 'Населенный пункт', 'Район', 'Адрес', 'Skype', 'Vkontakte', 'Facebook', 'Отдел церкви', ]


def get_hierarchy_chain(obj, l):
    d = OrderedDict()
    d['value'] = obj.get_full_name()
    d['id'] = obj.id
    l.append(d)
    master = obj.master
    if master:
        get_hierarchy_chain(master, l)


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
    departments = models.ManyToManyField('hierarchy.Department', related_name='userss')
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
        return reverse('account', args=(self.id,))

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

    @property
    def hierarchy_chain(self):
        l = list()
        get_hierarchy_chain(self, l)
        return l

    @property
    def has_disciples(self):
        return self.disciples.exists()

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
    def fields(self):
        l = OrderedDict()

        d = OrderedDict()
        d['value'] = self.id
        l['id'] = d

        d = OrderedDict()
        d['value'] = self.fullname
        l['fullname'] = d

        d = OrderedDict()
        d['value'] = self.short_fullname
        l['short_fullname'] = d

        d = OrderedDict()
        d['value'] = self.email
        l['email'] = d

        d = OrderedDict()
        if self.born_date:

            d['value'] = self.born_date
        else:
            d['value'] = ''
        l['born_date'] = d

        d = OrderedDict()
        d['value'] = self.phone_number
        l['phone_number'] = d

        d = OrderedDict()
        d['value'] = self.country
        l['country'] = d

        d = OrderedDict()
        d['value'] = self.region
        l['region'] = d

        d = OrderedDict()
        d['value'] = self.city
        l['city'] = d

        d = OrderedDict()
        d['value'] = self.district
        l['district'] = d

        d = OrderedDict()
        d['value'] = self.address
        l['address'] = d

        d = OrderedDict()
        d['value'] = ''
        if self.hierarchy:
            d['value'] = self.hierarchy.title
        l['hierarchy'] = d

        d = OrderedDict()
        d['value'] = ''
        if self.master:
            d['value'] = self.master.fullname
        l['master'] = d

        d = OrderedDict()
        d['value'] = ''
        if self.master:
            d['value'] = self.master.hierarchy.title
        l['master_hierarchy'] = d

        d = OrderedDict()
        if self.department:
            d['value'] = ''.join(self.departments.values_list('title', flat=True))
        else:
            d['value'] = ''
        l['department'] = d

        # s = OrderedDict()
        d = OrderedDict()
        d['skype'] = self.skype
        d['vkontakte'] = self.vkontakte
        d['facebook'] = self.facebook
        d['odnoklassniki'] = self.odnoklassniki
        l['social'] = d

        d = OrderedDict()
        d['value'] = self.repentance_date
        l['repentance_date'] = d

        d = OrderedDict()
        d['value'] = self.coming_date
        l['coming_date'] = d

        d = OrderedDict()
        sl = list()
        if self.divisions:
            for division in self.divisions.all():
                sl.append(division.title)
            d['value'] = ','.join(sl)
        else:
            d['value'] = ''
        l['divisions'] = d

        d = OrderedDict()
        d['value'] = self.description
        l['description'] = d
        return l

    @property
    def division_fields(self):
        l = OrderedDict()
        for division in self.divisions.all():
            d = OrderedDict()
            d['value'] = True
            l[division.title] = d
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
    def short_fullname(self):
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

    @property
    def hierarchy_name(self):
        return self.hierarchy.title

    @property
    def attrs(self):
        l = ['Ответственный', 'Отдел', 'Город', 'Номер телефона',
             'Количество прозвонов за неделю', 'Посмотреть прозвоны']
        return l

    @property
    def department_title(self):
        l = ''.join(self.department.values_list('title', flat=True))
        return l

    @property
    def partnerships_info(self):
        l = OrderedDict()
        try:
            p = self.partnership
            if p and p.level <= Partnership.MANAGER:
                l['is_responsible'] = True
                l['responsible'] = self.partnership.id
            else:
                l['is_responsible'] = False
                l['responsible'] = self.partnership.id
        except Exception:
            l['is_responsible'] = False
            l['responsible'] = ''
        # if self.partnership and self.partnership.level <= Partnership.MANAGER:
        #    l['is_responsible'] = True
        #    l['responsible'] = self.partnership.id
        return l


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
