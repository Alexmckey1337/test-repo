# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-15 08:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('summit', '0020_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='summittype',
            name='club_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='Club name'),
        ),
    ]
