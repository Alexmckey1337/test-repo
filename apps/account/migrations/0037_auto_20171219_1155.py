# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-19 11:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0036_customuser_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='hhome_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uusers', to='group.HomeGroup', verbose_name='Home group'),
        ),
    ]
