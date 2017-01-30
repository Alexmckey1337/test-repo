# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_church_columns(apps, schema_editor):
    Church_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    ch = Category.objects.create(title='churches', common=True)

    Church_columns.objects.bulk_create([
        Church_columns(title='title', verbose_title='Название Церкви', ordering_title='title', number=1, active=True,
                       editable=False, category_id=ch.id),
        Church_columns(title='department', verbose_title='Отдел', ordering_title='department__title', number=2,
                       active=True, editable=True, category_id=ch.id),
        Church_columns(title='city', verbose_title='Город', ordering_title='city', number=3, active=True,
                       editable=True, category_id=ch.id),
        Church_columns(title='pastor', verbose_title='Пастор Церкви', ordering_title='pastor__last_name', number=4,
                       active=True, editable=True, category_id=ch.id),
        Church_columns(title='is_open', verbose_title='Открыта', ordering_title='is_open', number=5, active=True,
                       editable=True, category_id=ch.id),
        Church_columns(title='address', verbose_title='Адрес', ordering_title='address', number=6, active=True,
                       editable=True, category_id=ch.id),
        Church_columns(title='phone_number', verbose_title='Телефонный номер', ordering_title='phone_number',
                       number=7, active=True, editable=True, category_id=ch.id),
        Church_columns(title='website', verbose_title='Адрес сайта', ordering_title='website',
                       number=8, active=True, editable=True, category_id=ch.id),
        Church_columns(title='count_groups', verbose_title='Количество групп', ordering_title='count_groups',
                       number=9, active=True, editable=True, category_id=ch.id),
        Church_columns(title='count_users', verbose_title='Количество людей', ordering_title='count_users',
                       number=10, active=True, editable=True, category_id=ch.id)
    ])


def create_homegroup_columns(apps, schema_editor):
    HomeGroup_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    hg = Category.objects.create(title='home_groups', common=True)

    HomeGroup_columns.objects.bulk_create([
        HomeGroup_columns(title='title', verbose_title='Название Группы', ordering_title='title', number=1,
                          active=True, editable=False, category_id=hg.id),
        HomeGroup_columns(title='church', verbose_title='Церковь', ordering_title='church__title', number=2,
                          active=True, editable=True, category_id=hg.id),
        HomeGroup_columns(title='city', verbose_title='Город', ordering_title='city', number=3,
                          active=True, editable=True, category_id=hg.id),
        HomeGroup_columns(title='leader', verbose_title='Лидер', ordering_title='leader__last_name', number=4,
                          active=True, editable=True, category_id=hg.id),
        HomeGroup_columns(title='opening_date', verbose_title='Дата открытия', ordering_title='opening_date',
                          number=5, active=True, editable=True, category_id=hg.id),
        HomeGroup_columns(title='address', verbose_title='Адрес', ordering_title='address', number=6,
                          active=True, editable=True, category_id=hg.id),
        HomeGroup_columns(title='phone_number', verbose_title='Телефонный номер', ordering_title='phone_number',
                          number=7, active=True, editable=True, category_id=hg.id),
        HomeGroup_columns(title='website', verbose_title='Адрес сайта', ordering_title='website', number=8,
                          active=True, editable=True, category_id=hg.id)
    ])


def delete_church_columns(apps, schema_editor):
    Church_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    Church_columns.objects.filter(category__title='churches').delete()
    Category.objects.filter(title="churches").delete()


def delete_homegroup_columns(apps, schema_editor):
    HomeGroup_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    HomeGroup_columns.objects.filter(category__title='home_groups').delete()
    Category.objects.filter(title="home_groups").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_auto_20170120_1046'),
        ('navigation', '0002_auto_20160922_1056')
    ]

    operations = [
        migrations.RunPython(create_church_columns, delete_church_columns),
        migrations.RunPython(create_homegroup_columns, delete_homegroup_columns),
    ]
