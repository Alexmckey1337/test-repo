# -*- coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict
from datetime import timedelta

from django.contrib.auth.models import User, UserManager
from django.db import models
from django.db.models import signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from event.models import EventAnket
from navigation.models import Table
from tv_crm.models import LastCall

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


@python_2_unicode_compatible
class CustomUser(User):
    middle_name = models.CharField(max_length=40, blank=True)
    phone_number = models.CharField(max_length=13, blank=True)
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
    department = models.ForeignKey('hierarchy.Department', related_name='users', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    hierarchy = models.ForeignKey('hierarchy.Hierarchy', related_name='users', null=True, blank=True,
                                  on_delete=models.SET_NULL)
    master = models.ForeignKey('self', related_name='disciples', null=True, blank=True, on_delete=models.SET_NULL)
    repentance_date = models.DateField(blank=True, null=True)
    coming_date = models.DateField(blank=True, null=True)
    hierarchy_order = models.BigIntegerField(blank=True, null=True)
    activation_key = models.CharField(max_length=40, blank=True)

    summit_consultants = models.ManyToManyField(
        'summit.SummitType', related_name='users',
        through='summit.SummitUserConsultant', through_fields=('user', 'summit_type'))

    objects = UserManager()

    def __str__(self):
        return self.fullname

    class Meta:
        ordering = ['-date_joined']

    def get_absolute_url(self):
        return '/account/{}/'.format(self.id)

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def hierarchy_chain(self):
        l = list()
        get_hierarchy_chain(self, l)
        return l

    @property
    def has_disciples(self):
        return self.disciples.exists()

    @property
    def column_table(self):
        l = OrderedDict()
        if self.table:
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
            d['value'] = self.department.title
        else:
            d['value'] = ''
        l['department'] = d

        d = OrderedDict()
        if self.additional_phones.exists():
            d['value'] = self.additional_phones.first().number
        else:
            d['value'] = ''
        l[u'additional_phone'] = d

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
    def last_week_calls(self):
        day = timezone.now().date() - timedelta(days=7)
        count = LastCall.objects.filter(
            user__master=self,
            user__hierarchy__level=4,
            date__gte=day, date__lte=(timezone.now().date())).count()
        return count

    @property
    def attrs(self):
        l = ['Ответственный', 'Отдел', 'Город', 'Номер телефона',
             'Количество прозвонов за неделю', 'Посмотреть прозвоны']
        return l

    @property
    def department_title(self):
        l = self.department.title
        return l

    @property
    def partnerships_info(self):
        l = OrderedDict()
        try:
            p = self.partnership
            if p and p.is_responsible:
                l['is_responsible'] = True
                l['responsible'] = self.partnership.id
            else:
                l['is_responsible'] = False
                l['responsible'] = self.partnership.id
        except Exception:
            l['is_responsible'] = False
            l['responsible'] = ''
        # if self.partnership and self.partnership.is_responsible:
        #    l['is_responsible'] = True
        #    l['responsible'] = self.partnership.id
        return l


@python_2_unicode_compatible
class AdditionalPhoneNumber(models.Model):
    user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, related_name='additional_phones',
                             verbose_name=_('User'))
    number = models.CharField(_('Number'), max_length=255)

    class Meta:
        unique_together = ('user', 'number')
        verbose_name = _('Additional Phone Number')
        verbose_name_plural = _('Additional Phone Numbers')

    def __str__(self):
        return self.number


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
            birth_day_notification = Notification.objects.get(theme__birth_day=True, user=instance)
            birth_day_notification.date = date
            birth_day_notification.save()
        except Notification.DoesNotExist:
            # description = "Сегодня свой день рождения отмечает %s." % instance.fullname
            Notification.objects.create(date=date,
                                        user=instance,
                                        theme=birth_day_notification_theme)
    from report.models import UserReport
    Table.objects.get_or_create(user=instance)
    EventAnket.objects.get_or_create(user=instance)
    UserReport.objects.get_or_create(user=instance)
