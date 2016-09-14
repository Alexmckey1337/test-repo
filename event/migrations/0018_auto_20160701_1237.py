# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-01 09:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0017_auto_20160629_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='from_date',
            field=models.DateField(default=datetime.date(2016, 7, 1)),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.datetime(2016, 7, 1, 9, 37, 38, 31744, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='to_date',
            field=models.DateField(default=datetime.date(2016, 7, 1)),
        ),
        migrations.AlterField(
            model_name='week',
            name='from_date',
            field=models.DateField(default=datetime.date(2016, 7, 1)),
        ),
        migrations.AlterField(
            model_name='week',
            name='to_date',
            field=models.DateField(default=datetime.date(2016, 7, 1)),
        ),
    ]
