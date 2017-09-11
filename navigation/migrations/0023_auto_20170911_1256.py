# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-11 12:56
from __future__ import unicode_literals

from django.db import migrations


def create_report_payments_columns(apps, schema_editor):
    Report_payments_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    report_payments = Category.objects.create(title='report_payments', common=True)

    Report_payments_columns.objects.bulk_create([
        Report_payments_columns(title='church', verbose_title='Церковь',
                                ordering_title='church_reports__church__title',
                                number=1, active=True, editable=False, category_id=report_payments.id),
        Report_payments_columns(title='sum_str', verbose_title='Сумма', ordering_title='sum', number=2,
                                active=True, editable=True, category_id=report_payments.id),
        Report_payments_columns(title='manager', verbose_title='Менеджер', ordering_title='manager__user__last_name',
                                number=3, active=True, editable=True, category_id=report_payments.id),
        Report_payments_columns(title='description', verbose_title='Примечание', ordering_title='description',
                                number=4, active=True, editable=True, category_id=report_payments.id),
        Report_payments_columns(title='sent_date', verbose_title='Дата поступления', ordering_title='sent_date',
                                number=5, active=True, editable=True, category_id=report_payments.id),
        Report_payments_columns(title='report_date', verbose_title='Дата подачи отчета',
                                ordering_title='church_reports__date',
                                number=6, active=True, editable=True, category_id=report_payments.id),
        Report_payments_columns(title='pastor_fio', verbose_title='Пастор',
                                ordering_title='church_reports__church__pastor__last_name',
                                number=7, active=True, editable=True, category_id=report_payments.id),
        Report_payments_columns(title='created_at', verbose_title='Дата создания', ordering_title='created_at',
                                number=8, active=True, editable=True, category_id=report_payments.id),
    ])


def delete_report_payments_columns(apps, schema_editor):
    Deal_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    Deal_columns.objects.filter(category__title='report_payments').delete()
    Category.objects.filter(title="reports_payments").delete()


class Migration(migrations.Migration):
    dependencies = [
        ('navigation', '0022_auto_20170907_1543'),
    ]

    operations = [
        migrations.RunPython(create_report_payments_columns, delete_report_payments_columns)
    ]
