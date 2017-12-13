# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-01 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('partnership', '0018_partnership_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnership',
            name='level',
            field=models.PositiveSmallIntegerField(
                choices=[(0, 'Director'), (1, 'Supervisor'), (2, 'Manager'), (3, 'Partner')], default=3,
                verbose_name='Level'),
        ),
    ]