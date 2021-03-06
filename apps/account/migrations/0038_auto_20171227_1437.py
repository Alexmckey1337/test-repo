# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-27 14:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0037_auto_20171219_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='managers',
            field=models.ManyToManyField(blank=True, related_name='_customuser_managers_+', to='account.CustomUser', verbose_name='Manager'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='skinz', to='account.CustomUser', verbose_name='Manager'),
        ),
    ]
