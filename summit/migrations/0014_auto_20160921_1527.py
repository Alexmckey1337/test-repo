# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-21 12:27
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0013_auto_20160914_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summitanket',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
