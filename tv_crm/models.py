# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models
from collections import OrderedDict


class LastCall(models.Model):
    user = models.ForeignKey('account.CustomUser', related_name='last_call', unique=True)
    last_responce = models.TextField(blank=True)
    date = models.DateField(auto_now=True)

    class Meta:
        ordering = ['date']

    @property
    def user_info(self):
        l = OrderedDict()

        l['user_fullname'] = ''
        if self.user.fullname:
            l['user_fullname'] = self.user.fullname

        l['user_id'] = ''
        if self.user.id:
            l['user_id'] = self.user.id

        l['phone_number'] = ''
        if self.user.phone_number:
            l['phone_number'] = self.user.phone_number

        l['master_full_name'] = ''
        if self.user.master:
            l['master_full_name'] = self.user.master.fullname

        l['city'] = ''
        if self.user.city:
            l['city'] = self.user.city

        l['hierarchy'] = ''
        if self.user.hierarchy:
            l['hierarchy'] = self.user.hierarchy.title

        l['department'] = ''
        if self.user.department:
            l['department'] = self.user.department.title

        return l

    @property
    def attrs(self):
        l = [u'Ответственный', u'Имя',u'Отдел',u'Город', u'Иерархия', u'Дата последнего прозвона',u'Номер телефона',u'Результат последнего прозвона',]
        return l


class Synopsis(models.Model):
    hero = models.TextField()
    phone_number = models.TextField()
    interviewer = models.ForeignKey('account.CustomUser', related_name='user_synopsis')
    date = models.DateField(auto_now=True)
    history_description = models.TextField()
    diagnosis = models.TextField(blank=True)
    sick_docs = models.TextField(blank=True)
    sick_description = models.TextField(blank=True)
    healing_description = models.TextField(blank=True)
    how_to_know = models.TextField(blank=True)
    how_recovery = models.TextField(blank=True)
    recovery_information = models.TextField(blank=True)
    recovery_docs = models.TextField(blank=True)
    decision_description = models.TextField(blank=True)
    survey_date = models.TextField(blank=True)
    producer = models.TextField(blank=True)

    @property
    def hero_fullname(self):
        l = self.hero.fullname
        return l

    @property
    def interviewer_fullname(self):
        l = self.interviewer.fullname
        return l

    @property
    def fields(self):
        l = OrderedDict()

        d = OrderedDict()
        d['value'] = self.interviewer.fullname
        d['change'] = False
        d['verbose'] = 'interviewer_fullname'
        l[u'Кто составил синопсис'] = d

        d = OrderedDict()
        d['value'] = self.hero
        d['change'] = True
        d['verbose'] = 'hero'
        l[u'ФИО'] = d

        d = OrderedDict()
        d['value'] = self.phone_number
        d['change'] = True
        d['verbose'] = 'phone_number'
        l[u'Телефоны'] = d

        d = OrderedDict()
        d['value'] = self.date
        d['change'] = False
        d['verbose'] = 'date'
        l[u'Дата'] = d

        d = OrderedDict()
        d['value'] = self.history_description
        d['change'] = True
        d['verbose'] = 'history_description'
        l[u'Суть истории'] = d

        d = OrderedDict()
        d['value'] = self.diagnosis
        d['change'] = True
        d['verbose'] = 'diagnosis'
        l[u'Информация про диагноз'] = d

        d = OrderedDict()
        d['value'] = self.sick_docs
        d['change'] = True
        d['verbose'] = 'sick_docs'
        l[u'Документы про болезнь'] = d

        d = OrderedDict()
        d['value'] = self.sick_description
        d['change'] = True
        d['verbose'] = 'sick_description'
        l[u'Описание болезни'] = d

        d = OrderedDict()
        d['value'] = self.healing_description
        d['change'] = True
        d['verbose'] = 'healing_description'
        l[u'Проходили ли лечение, выводы врачей'] = d

        d = OrderedDict()
        d['value'] = self.how_to_know
        d['change'] = True
        d['verbose'] = 'how_to_know'
        l[u'Как узнали о ДЦ "Возрождение"'] = d

        d = OrderedDict()
        d['value'] = self.how_recovery
        d['change'] = True
        d['verbose'] = 'how_recovery'
        l[u'Как получили исцеление или чудо'] = d

        d = OrderedDict()
        d['value'] = self.recovery_information
        d['change'] = True
        d['verbose'] = 'recovery_information'
        l[u'Кто молился, дата служения'] = d

        d = OrderedDict()
        d['value'] = self.recovery_docs
        d['change'] = True
        d['verbose'] = 'recovery_docs'
        l[u'Документы подтверждающие исцеление '] = d

        d = OrderedDict()
        d['value'] = self.decision_description
        d['change'] = True
        d['verbose'] = 'decision_description'
        l[u'Решение по сьемке материала '] = d

        d = OrderedDict()
        d['value'] = self.survey_date
        d['change'] = True
        d['verbose'] = 'survey_date'
        l[u'Дата сьемки'] = d

        d = OrderedDict()
        d['value'] = self.producer
        d['change'] = True
        d['verbose'] = 'producer'
        l[u'Режисер'] = d

        return l
