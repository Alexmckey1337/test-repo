# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-13 13:12
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0012_auto_20160613_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=timezone.now),
        ),
    ]
