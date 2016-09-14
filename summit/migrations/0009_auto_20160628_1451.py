# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-28 11:51
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0008_auto_20160621_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='summitanket',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='date',
            field=models.DateField(default=datetime.date(2016, 6, 28)),
        ),
    ]
