# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-01 08:40
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0003_auto_20160531_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnership',
            name='date',
            field=models.DateField(default=timezone.now),
        ),
    ]
