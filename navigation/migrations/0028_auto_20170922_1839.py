# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-22 18:39
from __future__ import unicode_literals

from django.db import migrations


def Change_deals_payments_manager_ordering(apps, schema_editor):
    Deals_payments_columns = apps.get_model('navigation', 'ColumnType')

    full_name_column = Deals_payments_columns.objects.filter(category__title='payment').filter(title='manager')
    full_name_column.update(ordering_title='manager__last_name')


def Change_reports_payments_manager_ordering(apps, schema_editor):
    Deals_payments_columns = apps.get_model('navigation', 'ColumnType')

    full_name_column = Deals_payments_columns.objects.filter(category__title='report_payments').filter(title='manager')
    full_name_column.update(ordering_title='manager__last_name')


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0027_auto_20170918_1835'),
    ]

    operations = [
        migrations.RunPython(Change_deals_payments_manager_ordering),
        migrations.RunPython(Change_reports_payments_manager_ordering),
    ]
