# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-29 17:02
from __future__ import unicode_literals

from django.db import migrations


def create_meetings_summary_columns(apps, schema_editor):
    Meeting_summary_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    meeting_summary = Category.objects.create(title='meetings_summary', common=True)

    Meeting_summary_columns.objects.bulk_create([
        Meeting_summary_columns(title='owner', verbose_title='Лидер',
                                ordering_title='last_name',
                                number=1, active=True, editable=False, category_id=meeting_summary.id),
        Meeting_summary_columns(title='master', verbose_title='Ответственный',
                                ordering_title='master__last_name', number=2,
                                active=True, editable=True, category_id=meeting_summary.id),
        Meeting_summary_columns(title='meetings_submitted', verbose_title='Зполненные отчеты',
                                ordering_title='meetings_submitted',
                                number=3, active=True, editable=True, category_id=meeting_summary.id),
        Meeting_summary_columns(title='meetings_in_progress', verbose_title='Отчеты к заполнению',
                                ordering_title='meetings_in_progress',
                                number=4, active=True, editable=True, category_id=meeting_summary.id),
        Meeting_summary_columns(title='meetings_expired', verbose_title='Просроченные отчеты',
                                ordering_title='meetings_expired', number=5,
                                active=True, editable=True, category_id=meeting_summary.id),
    ])


def delete_meetings_summary_columns(apps, schema_editor):
    Meeting_summary_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    Meeting_summary_columns.objects.filter(category__title='meetings_summary').delete()
    Category.objects.filter(title="meetings_summary").delete()


class Migration(migrations.Migration):
    dependencies = [
        ('navigation', '0018_auto_20170828_1031'),
    ]

    operations = [
        migrations.RunPython(create_meetings_summary_columns, delete_meetings_summary_columns)
    ]
