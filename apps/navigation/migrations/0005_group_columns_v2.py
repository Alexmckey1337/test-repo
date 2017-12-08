# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_church_opening_date_column(apps, schema_editor):
    Church_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    ch = Category.objects.get(title='churches')

    Church_columns.objects.bulk_create([
        Church_columns(title='opening_date', verbose_title='Дата открытия', ordering_title='opening_date',
                       number=12, active=True, editable=True, category_id=ch.id)
    ])


def create_homegroup_count_users_column(apps, schema_editor):
    HomeGroup_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    hg = Category.objects.get(title='home_groups')

    HomeGroup_columns.objects.bulk_create([
        HomeGroup_columns(title='count_users', verbose_title='Количество людей', ordering_title='count_users',
                          number=9, active=True, editable=True, category_id=hg.id)
    ])


def delete_church_opening_date_column(apps, schema_editor):
    Church_columns = apps.get_model("navigation", "ColumnType")
    Church_columns.objects.filter(category__title='churches').filter(title='opening_date').delete()


def delete_homegroup_count_users_column(apps, schema_editor):
    HomeGroup_columns = apps.get_model("navigation", "ColumnType")
    HomeGroup_columns.objects.filter(category__title='home_groups').filter(title='count_users').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0004_auto_20170213_1538')
    ]

    operations = [
        migrations.RunPython(create_church_opening_date_column, delete_church_opening_date_column),
        migrations.RunPython(create_homegroup_count_users_column, delete_homegroup_count_users_column),
    ]
