# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-01 11:32
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0018_auto_20160701_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.datetime(2016, 7, 1, 11, 32, 22, 163327, tzinfo=utc)),
        ),
    ]