# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-21 12:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0014_auto_20160914_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnership',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
