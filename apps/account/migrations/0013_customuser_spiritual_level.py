# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-04 10:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_auto_20161212_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='spiritual_level',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Baby'), (2, 'Junior'), (3, 'Father')], default=1, verbose_name='Spiritual Level'),
        ),
    ]
