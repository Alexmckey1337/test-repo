# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_church_columns(apps, schema_editor):
    pass


def create_homegroup_columns(apps, schema_editor):
    pass


def delete_church_columns(apps, schema_editor):
    pass


def delete_homegroup_columns(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_auto_20170120_1046'),
    ]

    operations = [
        migrations.RunPython(create_church_columns, delete_church_columns),
        migrations.RunPython(create_homegroup_columns, delete_homegroup_columns),
    ]
