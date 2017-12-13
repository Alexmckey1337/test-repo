# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 13:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0026_auto_20170213_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='responsible',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disciples_deals', to='partnership.Partnership', verbose_name='Responsible of partner'),
        ),
    ]