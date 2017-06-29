# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-15 14:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0056_auto_20170614_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='summitattend',
            name='status',
            field=models.CharField(default='', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='summitattend',
            name='time',
            field=models.TimeField(null=True, verbose_name='Time'),
        ),
    ]