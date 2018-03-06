# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-04 12:29
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weekreport',
            name='from_date',
            field=models.DateField(default=timezone.now),
        ),
        migrations.AlterField(
            model_name='weekreport',
            name='to_date',
            field=models.DateField(default=timezone.now),
        ),
    ]
