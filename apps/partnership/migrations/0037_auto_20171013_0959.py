# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-13 09:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0035_auto_20171004_1634'),
        ('partnership', '0036_auto_20171012_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='uresponsible',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='udisciples_deals', to='account.CustomUser', verbose_name='Responsible of partner'),
        ),
        migrations.AddField(
            model_name='partnership',
            name='uresponsible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='udisciples', to='account.CustomUser'),
        ),
        migrations.AddField(
            model_name='partnershiplogs',
            name='uresponsible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ulogs_disciples', to='account.CustomUser'),
        ),
    ]
