# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-17 07:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0007_auto_20160613_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weekreport',
            name='from_date',
            field=models.DateField(default=datetime.date(2016, 6, 17)),
        ),
        migrations.AlterField(
            model_name='weekreport',
            name='to_date',
            field=models.DateField(default=datetime.date(2016, 6, 17)),
        ),
    ]
