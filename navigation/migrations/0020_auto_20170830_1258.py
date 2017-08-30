# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-30 12:58
from __future__ import unicode_literals

from django.db import migrations


def create_meetings_summary_columns(apps, schema_editor):
    Reports_summary_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    reports_summary = Category.objects.create(title='reports_summary', common=True)

    Reports_summary_columns.objects.bulk_create([
        Reports_summary_columns(title='pastor', verbose_title='Пастор',
                                ordering_title='last_name',
                                number=1, active=True, editable=False, category_id=reports_summary.id),
        Reports_summary_columns(title='master', verbose_title='Ответственный',
                                ordering_title='master__last_name', number=2,
                                active=True, editable=True, category_id=reports_summary.id),
        Reports_summary_columns(title='meetings_submitted', verbose_title='Заполненные отчеты',
                                ordering_title='meetings_submitted',
                                number=3, active=True, editable=True, category_id=reports_summary.id),
        Reports_summary_columns(title='meetings_in_progress', verbose_title='Отчеты к заполнению',
                                ordering_title='meetings_in_progress',
                                number=4, active=True, editable=True, category_id=reports_summary.id),
        Reports_summary_columns(title='meetings_expired', verbose_title='Просроченные отчеты',
                                ordering_title='meetings_expired', number=5,
                                active=True, editable=True, category_id=reports_summary.id),
    ])


def delete_meetings_summary_columns(apps, schema_editor):
    Reports_summary_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    Reports_summary_columns.objects.filter(category__title='reports_summary').delete()
    Category.objects.filter(title="reports_summary").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0019_auto_20170829_1702'),
    ]

    operations = [
        migrations.RunPython(create_meetings_summary_columns, delete_meetings_summary_columns)
    ]
