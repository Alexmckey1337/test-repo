# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-13 08:41
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0011_auto_20160613_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.datetime(2016, 6, 13, 8, 41, 10, 546016, tzinfo=utc)),
        ),
    ]