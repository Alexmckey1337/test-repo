# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-04 13:19
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_auto_20170703_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='logrecord',
            name='raw_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, verbose_name='raw data'),
        ),
    ]