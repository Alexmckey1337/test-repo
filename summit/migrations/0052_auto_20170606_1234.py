# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-06 12:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0051_auto_20170530_1530'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='summitvisitorlocation',
            options={'ordering': ('-id',), 'verbose_name': 'Summit User Location', 'verbose_name_plural': 'Summit Users Location'},
        ),
        migrations.AddField(
            model_name='summiteventtable',
            name='hide_time',
            field=models.BooleanField(default=False, verbose_name='Не отображать время'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='spiritual_level',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Renegade'), (1, 'Baby'), (2, 'Junior'), (3, 'Father')], default=1, verbose_name='Spiritual Level'),
        ),
    ]
