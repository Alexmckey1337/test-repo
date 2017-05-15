# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-05 07:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0042_auto_20170504_1622'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summitanket',
            name='protected',
        ),
        migrations.RemoveField(
            model_name='summitanket',
            name='retards',
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='bishop',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Name of bishop'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='date',
            field=models.DateField(auto_now_add=True, verbose_name='Date created'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='department',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Titles of departments'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='first_name',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Fisrt name'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='hierarchy_title',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Title of hierarchy'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='last_name',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='pastor',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Name of pastor'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='responsible',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Name of master'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='sotnik',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Name of sotnik'),
        ),
    ]