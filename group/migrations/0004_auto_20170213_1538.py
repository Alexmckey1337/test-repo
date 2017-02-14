# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0003_columns'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='church',
            options={'ordering': ['-opening_date', '-id'], 'verbose_name': 'Church', 'verbose_name_plural': 'Churches'},
        ),
        migrations.AlterModelOptions(
            name='homegroup',
            options={'ordering': ['-opening_date', '-id'], 'verbose_name': 'Home Group', 'verbose_name_plural': 'Home Groups'},
        ),
        migrations.AlterField(
            model_name='church',
            name='country',
            field=models.CharField(max_length=50, verbose_name='Country'),
        ),
    ]
