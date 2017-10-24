# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-13 12:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0040_rename_uresponsible_to_responsible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='responsible',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disciples_deals', to='account.CustomUser', verbose_name='Responsible of partner'),
        ),
        migrations.AlterField(
            model_name='partnership',
            name='responsible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='partner_disciples', to='account.CustomUser'),
        ),
        migrations.AlterField(
            model_name='partnershiplogs',
            name='responsible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partner_disciples_logs', to='account.CustomUser'),
        ),
    ]
