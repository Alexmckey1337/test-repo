# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-17 07:29
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0006_auto_20160613_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='summitanket',
            name='sotnik',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='date',
            field=models.DateField(default=timezone.now),
        ),
    ]
