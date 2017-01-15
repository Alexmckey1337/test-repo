# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-04 13:54
from __future__ import unicode_literals

from django.db import migrations


def create_currencies(apps, schema_editor):
    Currency = apps.get_model("payment", "Currency")

    Currency.objects.bulk_create([
        Currency(name='Доллар США', code='usd', short_name='дол.', symbol='$', output_format='{symbol}{value}'),
        Currency(name='Гривна', code='uah', short_name='грн.', symbol='₴', output_format='{value} {short_name}'),
        Currency(name='Евро', code='eur', short_name='eвр.', symbol='€', output_format='{value} {symbol}'),
        Currency(name='Рубль', code='rur', short_name='руб.', symbol='₽', output_format='{value} {short_name}'),
    ])


def delete_currencies(apps, schema_editor):
    Currency = apps.get_model("payment", "Currency")

    Currency.objects.filter(code__in=('usd', 'uah', 'eur', 'rur')).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_currency'),
    ]

    operations = [
        migrations.RunPython(create_currencies, delete_currencies),
    ]
