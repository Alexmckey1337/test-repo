# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-04 13:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_auto_20161228_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('code', models.SlugField(max_length=8, unique=True, verbose_name='Code')),
                ('short_name', models.CharField(max_length=8, verbose_name='Short name')),
                ('symbol', models.CharField(blank=True, max_length=8, verbose_name='Symbol')),
                ('output_format', models.CharField(help_text='Possible values: <br /><br />{value} — sum, <br />{symbol} — currency symbol, <br />{short_name} — short name of currency, <br />{name} — full name of currency', max_length=255, verbose_name='Output format')),
            ],
            options={
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currencies',
            },
        ),
    ]