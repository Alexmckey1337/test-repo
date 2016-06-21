# -*- coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import post_save
from collections import OrderedDict
from django.utils import timezone
from datetime import timedelta
from tv_crm.models import LastCall
from event.models import EventAnket
from django.db.models import signals
from django.dispatch import receiver
from navigation.models import Table

COMMON = ['Имя', 'Фамилия', 'Отчество','Email','Телефон', 'Дата рождения', 'Иерархия','Отдел',
          'Страна', 'Область', 'Населенный пункт', 'Район','Адрес', 'Skype', 'Vkontakte', 'Facebook', 'Отдел церкви',]


def get_hierarchy_chain(obj, l):
    d = OrderedDict()
    d['value'] = obj.get_full_name()
    d['id'] = obj.id
    l.append(d)
    master = obj.master
    if master:
        get_hierarchy_chain(master, l)


class CustomUser(User):
    middle_name = models.CharField(max_length=40, default='', blank=True)
    phone_number = models.CharField(max_length=13, default='', blank=True, null=True)
    skype = models.CharField(max_length=50, default='', null=True, blank=True)
    country = models.CharField(max_length=50, default='', blank=True)
    region = models.CharField(max_length=50, default='', blank=True)
    city = models.CharField(max_length=50, default='', blank=True)
    district = models.CharField(max_length=50, default='', blank=True)
    address = models.CharField(max_length=300, default='', null=True, blank=True)
    born_date = models.DateField(blank=True, null=True)
    facebook = models.URLField(default='', blank=True, null=True)
    vkontakte = models.URLField(default='', blank=True, null=True)
    odnoklassniki = models.URLField(default='', blank=True, null=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    image_source = models.ImageField(upload_to='images/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey('hierarchy.Department', related_name='users', null=True, blank=True, on_delete=models.SET_NULL)
    hierarchy = models.ForeignKey('hierarchy.Hierarchy', related_name='users', null=True, blank=True, on_delete=models.SET_NULL)
    master = models.ForeignKey('self', related_name='disciples', null=True, blank=True, on_delete=models.SET_NULL)
    repentance_date = models.DateField(blank=True, null=True)
    coming_date = models.DateField(blank=True, null=True)
    hierarchy_order = models.BigIntegerField(blank=True, null=True)
    activation_key = models.CharField(max_length=40, blank=True)

    objects = UserManager()

    def __unicode__(self):
        return self.username

    class Meta:
        ordering = ['-date_joined']

    @property
    def hierarchy_chain(self):
        l = list()
        get_hierarchy_chain(self, l)
        return l

    @property
    def has_disciples(self):
        if self.disciples.all():
            return True
        else:
            return False

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
        l[u'id'] = d

        d = OrderedDict()
        d['value'] = self.fullname
        l[u'fullname'] = d

        d = OrderedDict()
        d['value'] = self.short_fullname
        l[u'short_fullname'] = d

        d = OrderedDict()
        d['value'] = self.email
        l[u'email'] = d

        d = OrderedDict()
        if self.born_date:

            d['value'] = self.born_date
        else:
            d['value'] = ''
        l[u'born_date'] = d

        d = OrderedDict()
        d['value'] = self.phone_number
        l[u'phone_number'] = d

        d = OrderedDict()
        d['value'] = self.country
        l[u'country'] = d

        d = OrderedDict()
        d['value'] = self.region
        l[u'region'] = d

        d = OrderedDict()
        d['value'] = self.city
        l[u'city'] = d

        d = OrderedDict()
        d['value'] = self.district
        l[u'district'] = d

        d = OrderedDict()
        d['value'] = self.address
        l[u'address'] = d

        d = OrderedDict()
        d['value'] = ''
        if self.hierarchy:
            d['value'] = self.hierarchy.title
        l[u'hierarchy'] = d

        d = OrderedDict()
        d['value'] = ''
        if self.master:
            d['value'] = self.master.fullname
        l[u'master'] = d

        d = OrderedDict()
        d['value'] = ''
        if self.master:
            d['value'] = self.master.hierarchy.title
        l[u'master_hierarchy'] = d

        d = OrderedDict()
        if self.department:
            d['value'] = self.department.title
        else:
            d['value'] = ''
        l[u'department'] = d

        #s = OrderedDict()
        d = OrderedDict()
        d['skype'] = self.skype
        d['vkontakte'] = self.vkontakte
        d['facebook'] = self.facebook
        d['odnoklassniki'] = self.odnoklassniki
        l[u'social'] = d

        d = OrderedDict()
        d['value'] = self.repentance_date
        l[u'repentance_date'] = d

        d = OrderedDict()
        d['value'] = self.coming_date
        l[u'coming_date'] = d

        d = OrderedDict()
        sl = list()
        if self.divisions:
            for division in self.divisions.all():
                sl.append(division.title)
            d['value'] = ','.join(sl)
        else:
            d['value'] = ''
        l[u'divisions'] = d

        d = OrderedDict()
        d['value'] = self.description
        l[u'description'] = d
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
        return self.last_name.strip() + ' ' + self.first_name.strip() + ' ' + self.middle_name.strip()

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
        l = [u'Ответственный', u'Отдел', u'Город', u'Номер телефона',
             u'Количество прозвонов за неделю', u'Посмотреть прозвоны']
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
                l[u'is_responsible'] = True
                l[u'responsible'] = self.partnership.id
            else:
                l[u'is_responsible'] = False
                l[u'responsible'] = self.partnership.id
        except Exception:
            l[u'is_responsible'] = False
            l[u'responsible'] = ''
        #if self.partnership and self.partnership.is_responsible:
        #    l[u'is_responsible'] = True
        #    l[u'responsible'] = self.partnership.id
        return l


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
            description = u"Сегодня свой день рождения отмечает %s." % instance.fullname
            birth_day_notification = Notification.objects.create(date=date,
                                                                 user=instance,
                                                                 theme=birth_day_notification_theme)
    from report.models import UserReport
    try:
        table = Table.objects.get(user=instance)
    except Table.DoesNotExist:
        table = Table.objects.create(user=instance)
    try:
        event_anket = EventAnket.objects.get(user=instance)
    except EventAnket.DoesNotExist:
        event_anket = EventAnket.objects.create(user=instance)
    try:
        user_report = UserReport.objects.get(user=instance)
    except UserReport.DoesNotExist:
        user_report = UserReport.objects.create(user=instance)
