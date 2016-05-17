# -*- coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import post_save
from collections import OrderedDict
from report.models import UserReport
from event.models import Event
from django.utils import timezone


VERBOSE_FIELDS = OrderedDict([('Имя', 'first_name'),
             ('Фамилия', 'last_name'),
             ('Отчество', 'middle_name'),
             ('Email', 'email'),
             ('Телефон', 'phone_number'),
             ('Дата рождения', 'born_date'),
             ('Иерархия', 'hierarchy'),
             ('Отдел', 'department'),
             ('Страна', 'country'),
             ('Область', 'region'),
             ('Населенный пункт', 'city'),
             ('Район', 'district'),
             ('Адрес', 'address'),
             ('Skype', 'skype'),
             ('Vkontakte', 'vkontakte'),
             ('Facebook', 'facebook')])
'''VERBOSE_FIELDS = {'Имя': 'first_name',
                  'Фамилия': 'last_name',
                  'Отчество': 'middle_name',

                  'Email': 'email',
                  'Телефон': 'phone_number',
                  'Дата рождения': 'born_date',

                  'Иерархия': 'hierarchy',
                  'Отдел': 'department',

                  'Страна': 'country',
                  'Область': 'region',
                  'Населенный пункт': 'city',
                  'Район': 'district',
                  'Адрес': 'address',

                  'Skype': 'skype',
                  'Vkontakte': 'vkontakte',
                  'Facebook': 'facebook'}'''
def get_master(obj, l):
    master = obj.master
    d = OrderedDict()
    if master:
        d['value'] = master.fullname
        d['type'] = 'h'
        d['change'] = False
        d['verbose'] = 'master'
        l[master.hierarchy.title] = d
        get_master(master, l)


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
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey('hierarchy.Department', related_name='users', null=True, blank=True, on_delete=models.SET_NULL)
    hierarchy = models.ForeignKey('hierarchy.Hierarchy', related_name='users', null=True, blank=True, on_delete=models.SET_NULL)
    master = models.ForeignKey('self', related_name='disciples', null=True, blank=True, on_delete=models.SET_NULL)
    objects = UserManager()

    def __unicode__(self):
        return self.username
    class Meta:
        ordering = ['id']

    @property
    def common(self):
        l = VERBOSE_FIELDS
        return l

    @property
    def my_reports(self):
        l = OrderedDict()
        d = OrderedDict()
        d['value'] = self.fullname
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'fullname'
        l[u'ФИО'] = d

        d = OrderedDict()
        d['value'] = self.hierarchy.title
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'hierarchy'
        l[u'Иерархия'] = d
        current_month = timezone.now().date().month
        reports = UserReport.objects.filter(user=self, date__month=current_month).all()
        for report in reports: 

            title = report.event.title + '/' + str(report.date)
            d = OrderedDict()
            d['value'] = report.count
            d['type'] = 's'
            d['change'] = False
            d['verbose'] = 'count'
            l[title] = d
        return l

    @property
    def short(self):
        l = OrderedDict()

        d = OrderedDict()
        d['value'] = self.last_name
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'last_name'
        l[u'Фамилия'] = d

        d = OrderedDict()
        d['value'] = self.first_name
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'first_name'
        l[u'Имя'] = d

        d = OrderedDict()
        d['value'] = self.middle_name
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'middle_name'
        l[u'Отчество'] = d

        d = OrderedDict()
        d['value'] = self.email
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'email'
        l[u'Email'] = d

        d = OrderedDict()
        d['value'] = self.phone_number
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'phone_number'
        l[u'Телефон'] = d



        d = OrderedDict()
        d['value'] = self.hierarchy.title
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'hierarchy'
        l[u'Иерархия'] = d

        d = OrderedDict()
        d['value'] = self.department.title
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'department'
        l[u'Отдел'] = d
        return l



    @property
    def fields(self):
        l = OrderedDict()

        d = OrderedDict()
        d['value'] = self.last_name
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'last_name'
        l[u'Фамилия'] = d

        d = OrderedDict()
        d['value'] = self.first_name
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'first_name'
        l[u'Имя'] = d

        d = OrderedDict()
        d['value'] = self.middle_name
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'middle_name'
        l[u'Отчество'] = d

        d = OrderedDict()
        d['value'] = self.email
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'email'
        l[u'Email'] = d

        d = OrderedDict()
        if self.born_date:

            d['value'] = self.born_date
        else:
            d['value'] = ''
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'born_date'
        l[u'Дата рождения'] = d

        d = OrderedDict()
        d['value'] = self.phone_number
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'phone_number'
        l[u'Телефон'] = d

        d = OrderedDict()
        d['value'] = self.country
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'country'
        l[u'Страна'] = d
        
        d = OrderedDict()
        d['value'] = self.region
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'region'
        l[u'Область'] = d

        d = OrderedDict()
        d['value'] = self.city
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'city'
        l[u'Город'] = d
        
        d = OrderedDict()
        d['value'] = self.district
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'district'
        l[u'Район'] = d

        d = OrderedDict()
        d['value'] = self.address
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'address'
        l[u'Адрес'] = d

        d = OrderedDict()
        d['value'] = self.hierarchy.title
        d['type'] = 'h'
        d['change'] = False
        d['verbose'] = 'hierarchy'
        l[u'Иерархия'] = d

        d = OrderedDict()
        if self.department:
            d['value'] = self.department.title
        else:
            d['value'] = ''
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'department'
        l[u'Отдел'] = d

        d = OrderedDict()
        d['value'] = self.skype
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'skype'
        l[u'Skype'] = d

        d = OrderedDict()
        d['value'] = self.vkontakte
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'vkontakte'
        l[u'Вконтакте'] = d

        d = OrderedDict()
        d['value'] = self.facebook
        d['type'] = 's'
        d['change'] = False
        d['verbose'] = 'facebook'
        l[u'Facebook'] = d

        d = OrderedDict()
        d['value'] = self.description
        d['type'] = 't'
        d['change'] = False
        d['verbose'] = 'description'
        l[u'Примечание'] = d

        get_master(self, l)

        for status in self.statuses.all():
            d = OrderedDict()
            d['value'] = True
            d['type'] = 'b'
            d['change'] = False
            d['verbose'] = 'status.title'
            l[status.title] = d


        return l

    @property
    def fullname(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.middle_name

    @property
    def hierarchy_name(self):
        return self.hierarchy.title

def create_custom_user(sender, instance, created, **kwargs):
    if created:
        values = {}
        for field in sender._meta.local_fields:
            values[field.attname] = getattr(instance, field.attname)
        user = CustomUser(**values)
        user.save()

post_save.connect(create_custom_user, User)
