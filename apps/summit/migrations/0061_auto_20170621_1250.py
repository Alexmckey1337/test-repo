# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-21 12:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0060_summitattend_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summitattend',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created at'),
        ),
    ]
