# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-22 11:44
from __future__ import unicode_literals

from django.db import migrations
from treebeard.numconv import NumConv

alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def set_path(apps, schema_editor):
    nc = NumConv(len(alphabet), alphabet)
    CustomUser = apps.get_model("account", "CustomUser")

    # set path for root elements
    for i, user in enumerate(CustomUser.objects.filter(level=0), start=1):
        base_path = nc.int2str(i)
        user.path = '{0}{1}'.format(
            alphabet[0] * (6 - len(base_path)),
            base_path
        )
        user.depth = 1
        user.numchild = CustomUser.objects.filter(master=user).count()
        user.save()

    # set path for not root elements
    max_level = CustomUser.objects.order_by('-level').first()
    max_level = max_level.level if max_level else 0
    levels = range(1, max_level + 1)
    for level in levels:
        for master in CustomUser.objects.filter(level=level-1):
            for i, user in enumerate(CustomUser.objects.filter(master=master, level=level), start=1):
                base_path = nc.int2str(i)
                user.path = '{0}{1}{2}'.format(
                    master.path,
                    alphabet[0] * (6 - len(base_path)),
                    base_path
                )
                user.depth = level + 1
                user.numchild = CustomUser.objects.filter(master=user).count()
                user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0031_auto_20170822_1144'),
    ]

    operations = [
        migrations.RunPython(set_path, lambda a, s: 0),
    ]
