# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-10 14:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0006_auto_20160922_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='location.Country'),
        ),
        migrations.AlterField(
            model_name='city',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='location.Region'),
        ),
        migrations.AlterField(
            model_name='region',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='location.Country'),
        ),
    ]
