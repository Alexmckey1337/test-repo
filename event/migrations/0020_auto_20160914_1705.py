# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-09-14 14:05
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0019_auto_20160701_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='from_date',
            field=models.DateField(default=datetime.date(2016, 9, 14)),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.datetime(2016, 9, 14, 14, 5, 50, 29254, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='to_date',
            field=models.DateField(default=datetime.date(2016, 9, 14)),
        ),
        migrations.AlterField(
            model_name='week',
            name='from_date',
            field=models.DateField(default=datetime.date(2016, 9, 14)),
        ),
        migrations.AlterField(
            model_name='week',
            name='to_date',
            field=models.DateField(default=datetime.date(2016, 9, 14)),
        ),
        migrations.AlterField(
            model_name='week',
            name='week',
            field=models.IntegerField(default=37, unique=True),
        ),
    ]