# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-10 14:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0035_auto_20171109_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='columntype',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='columnTypes', to='navigation.Category'),
        ),
    ]
