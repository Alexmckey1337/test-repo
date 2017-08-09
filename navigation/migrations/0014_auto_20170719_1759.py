# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-19 17:59
from __future__ import unicode_literals

from django.db import migrations


def create_deal_columns(apps, schema_editor):
    Deal_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    deal = Category.objects.create(title='deal', common=True)

    Deal_columns.objects.bulk_create([
        Deal_columns(title='full_name', verbose_title='ФИО', ordering_title='partnership__user__last_name', number=1,
                     active=True, editable=True, category_id=deal.id),
        Deal_columns(title='date_created', verbose_title='Дата сделки', ordering_title='date_created', number=2,
                     active=True, editable=True, category_id=deal.id),
        Deal_columns(title='responsible', verbose_title='Менеджер', ordering_title='responsible__user__last_name',
                     number=3, active=True, editable=True, category_id=deal.id),
        Deal_columns(title='sum', verbose_title='Сумма', ordering_title='value',
                     number=4, active=True, editable=True, category_id=deal.id),
        Deal_columns(title='action', verbose_title='Действие', ordering_title='done',
                     number=6, active=True, editable=False, category_id=deal.id),
    ])


def delete_deal_columns(apps, schema_editor):
    Deal_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    Deal_columns.objects.filter(category__title='deal').delete()
    Category.objects.filter(title="deal").delete()


class Migration(migrations.Migration):
    dependencies = [
        ('navigation', '0013_auto_20170616_1611'),
    ]

    operations = [
        migrations.RunPython(create_deal_columns, delete_deal_columns),
    ]