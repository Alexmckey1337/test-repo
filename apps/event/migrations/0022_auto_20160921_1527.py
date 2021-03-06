# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-21 12:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import apps.event.models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0021_auto_20160914_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='from_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='to_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='week',
            name='from_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='week',
            name='to_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='week',
            name='week',
            field=models.IntegerField(default=apps.event.models.current_week, unique=True),
        ),
    ]
