# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-28 11:51
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0015_auto_20160621_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='from_date',
            field=models.DateField(default=datetime.date(2016, 6, 28)),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.datetime(2016, 6, 28, 11, 51, 53, 921802, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='to_date',
            field=models.DateField(default=datetime.date(2016, 6, 28)),
        ),
        migrations.AlterField(
            model_name='week',
            name='from_date',
            field=models.DateField(default=datetime.date(2016, 6, 28)),
        ),
        migrations.AlterField(
            model_name='week',
            name='to_date',
            field=models.DateField(default=datetime.date(2016, 6, 28)),
        ),
        migrations.AlterField(
            model_name='week',
            name='week',
            field=models.IntegerField(default=26, unique=True),
        ),
    ]