# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-19 11:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0013_auto_20171213_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='church',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, verbose_name='Номер телефона'),
        ),
    ]