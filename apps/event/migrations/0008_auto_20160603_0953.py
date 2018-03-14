# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-03 06:53
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0007_auto_20160601_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='from_date',
            field=models.DateField(default=timezone.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=timezone.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='to_date',
            field=models.DateField(default=timezone.now),
        ),
        migrations.AlterField(
            model_name='week',
            name='from_date',
            field=models.DateField(default=timezone.now),
        ),
        migrations.AlterField(
            model_name='week',
            name='to_date',
            field=models.DateField(default=timezone.now),
        ),
    ]
