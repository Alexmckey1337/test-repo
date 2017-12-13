# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-28 09:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0038_summitticket'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='summitticket',
            options={'ordering': ('summit', 'title'), 'verbose_name': 'Summit ticket', 'verbose_name_plural': 'List of summit tickets'},
        ),
        migrations.AlterField(
            model_name='summitticket',
            name='users',
            field=models.ManyToManyField(related_name='tickets', to='summit.SummitAnket', verbose_name='Users'),
        ),
    ]