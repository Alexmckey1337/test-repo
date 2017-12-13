# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-06 12:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0025_merge_20170518_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='spiritual_level',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Renegade'), (1, 'Baby'), (2, 'Junior'), (3, 'Father')], default=1, verbose_name='Spiritual Level'),
        ),
    ]