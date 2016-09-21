# -*- coding: utf-8
from __future__ import unicode_literals

import hashlib
import random
from datetime import timedelta

from django.utils import timezone

from account.models import CustomUser as User
from event.models import Event, Participation
from hierarchy.models import Hierarchy, Department
from report.models import UserReport as Report

H = {'1': 'Прихожанин',
     '2': 'Лидер',
     '3': 'Сотник',
     '4': 'Пастор',
     '5': 'Епископ',
     '6': 'Апостол',
     '7': 'Архонт'}

E = {'1': 'Понедельник',
     '2': 'Вторник',
     '3': 'Среда',
     '4': 'Четверг',
     '5': 'Пятница',
     '6': 'Суббота',
     '7': 'Воскресенье'}


def create_hierarchy():
    for key, value in H.items():
        hierarchy = Hierarchy.objects.create(level=int(key), title=value)
        hierarchy.save()
        print("Created:" + hierarchy.title)
    department = Department.objects.create(title='Киев')
    department.save()
    print("Created:" + department.title)
    return 'Done!'


def create_users(master, count=2):
    department = Department.objects.get(id=1)
    for i in range(count):
        hierarchy_level = master.hierarchy.level - 1
        hierarchy = Hierarchy.objects.filter(level=hierarchy_level).first()
        if hierarchy:
            salt = hashlib.sha1(str(random.random())).hexdigest()[:10]
            username = 'user%s' % salt
            user = User.objects.create(username=username,
                                       first_name=username,
                                       last_name=username,
                                       middle_name=username,
                                       department=department,
                                       hierarchy=hierarchy,
                                       master=master
                                       )
            user.save()
            print('Created: ' + user.username)
            create_users(user, count)
    return 'Done!'


def create_events():
    for key, value in E.items():
        event = Event.objects.create(day=int(key), title=value, active=True, cyclic=True)
        event.save()
        print("Created:" + event.title)
    return 'Done!'


def create_participations():
    users = User.objects.all()
    events = Event.objects.all()
    for user in users:
        for event in events:
            participation = Participation.objects.filter(user=user, event=event).first()
            if not participation:
                participation = Participation.objects.create(user=user, event=event, check=False)
                participation.save()
                print("Created participation: " + event.title + ',' + user.username)
    return 'Done'


def create_reports(weekday, delta=0):
    event = Event.objects.filter(day=weekday).first()
    users = User.objects.all()
    date = timezone.now().date() - timedelta(days=delta)
    for user in users:
        report = Report.objects.create(user=user, event=event, date=date)
        report.save()
        print("Created report: " + event.title + ',' + user.username)
    return "Done!"


def create():
    weekday = timezone.now().weekday()
    master = User.objects.filter(id=1).first()
    if master:
        create_hierarchy()
        create_users(master, 2)
        create_events()
        create_participations()
        create_reports(weekday)
