# -*- coding: utf-8
from __future__ import unicode_literals

from hierarchy.models import Hierarchy, Department

H = {'1': 'Прихожанин',
     '2': 'Лидер',
     '3': 'Сотник',
     '4': 'Пастор',
     '5': 'Епископ',
     '6': 'Апостол',
     '7': 'Архонт'}


def create():
    for key, value in H.items():
        hierarchy = Hierarchy.objects.create(level=int(key), title=value)
        hierarchy.save()
    department = Department.objects.create(title='Киев')
    department.save()
    return 'Done!'
