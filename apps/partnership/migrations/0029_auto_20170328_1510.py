# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-28 12:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0028_auto_20170213_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnership',
            name='need_text',
            field=models.CharField(blank=True, max_length=600, verbose_name='Need text'),
        ),
    ]