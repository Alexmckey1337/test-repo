# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-25 15:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0006_auto_20170613_1554'),
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
            name='city',
            field=models.CharField(max_length=50, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='church',
            name='country',
            field=models.CharField(max_length=50, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='church',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='churches', to='hierarchy.Department', verbose_name='Department'),
        ),
        migrations.AlterField(
            model_name='church',
            name='opening_date',
            field=models.DateField(default=datetime.date.today, verbose_name='Opening Date'),
        ),
        migrations.AlterField(
            model_name='church',
            name='pastor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='church', to='account.CustomUser', verbose_name='Pastor'),
        ),
        migrations.AlterField(
            model_name='church',
            name='phone_number',
            field=models.CharField(blank=True, max_length=13, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='church',
            name='title',
            field=models.CharField(blank=True, max_length=50, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='church',
            name='website',
            field=models.URLField(blank=True, verbose_name='Web Site'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='church',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_group', to='group.Church', verbose_name='Church'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='city',
            field=models.CharField(max_length=50, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='home_group', to='account.CustomUser', verbose_name='Leader'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='opening_date',
            field=models.DateField(default=datetime.date.today, verbose_name='Opening Date'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='phone_number',
            field=models.CharField(blank=True, max_length=13, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='title',
            field=models.CharField(blank=True, max_length=50, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='website',
            field=models.URLField(blank=True, verbose_name='Web Site'),
        ),
    ]
