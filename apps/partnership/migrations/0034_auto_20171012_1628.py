# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-12 16:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0033_auto_20170913_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partners', to='account.CustomUser'),
        ),
    ]
