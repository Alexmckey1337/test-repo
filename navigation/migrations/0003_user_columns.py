# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_user_column_types(apps, schema_editor):
    UserColumns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    category = Category.objects.get(id=1)

    UserColumns.objects.bulk_create([
        UserColumns(title='repentance_date', verbose_title='Дата Покаяния', ordering_title='repentance_date',
                    number=15, active=True, editable=True, category_id=category.id),
        UserColumns(title='spiritual_level', verbose_title='Духовный уровень', ordering_title='spiritual_level',
                    number=16, active=True, editable=True, category_id=category.id)])


def delete_user_column_types(apps, schema_editor):
    UserColumns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    UserColumns.objects.filter(columnType__title__in=['repentance_date', 'spiritual_level']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0002_auto_20160922_1056')
    ]

    operations = [
        migrations.RunPython(update_user_column_types, delete_user_column_types),
    ]
