# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-18 15:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0041_auto_20171013_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerrole',
            name='plan',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=12, null=True, verbose_name='Manager plan'),
        ),
    ]
