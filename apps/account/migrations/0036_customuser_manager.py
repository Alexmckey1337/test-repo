# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-27 16:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0035_auto_20171004_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='skins', to='account.CustomUser', verbose_name='Manager'),
        ),
    ]
