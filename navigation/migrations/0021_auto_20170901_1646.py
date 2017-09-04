# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-01 16:46
from __future__ import unicode_literals

from django.db import migrations


def create_partnership_summary_columns(apps, schema_editor):
    Partnership_summary_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    partnership_summary = Category.objects.create(title='partnership_summary', common=True)

    Partnership_summary_columns.objects.bulk_create([
        Partnership_summary_columns(title='manager', verbose_title='Менеджер',
                                    ordering_title='manager',
                                    number=1, active=True, editable=False, category_id=partnership_summary.id),
        Partnership_summary_columns(title='plan', verbose_title='План',
                                    ordering_title='plan', number=2,
                                    active=True, editable=True, category_id=partnership_summary.id),
        Partnership_summary_columns(title='potential_sum', verbose_title='Потенциал',
                                    ordering_title='potential_sum',
                                    number=3, active=True, editable=True, category_id=partnership_summary.id),
        Partnership_summary_columns(title='sum_deals', verbose_title='Сумма сделок',
                                    ordering_title='sum_deals',
                                    number=4, active=True, editable=True, category_id=partnership_summary.id),
        Partnership_summary_columns(title='sum_pay', verbose_title='Сумма платежей',
                                    ordering_title='sum_pay',
                                    number=5, active=True, editable=True, category_id=partnership_summary.id),
        Partnership_summary_columns(title='percent_of_plan', verbose_title='% выполнения плана',
                                    ordering_title='percent_of_plan', number=6,
                                    active=True, editable=True, category_id=partnership_summary.id),
        Partnership_summary_columns(title='total_partners', verbose_title='Всего партнеров',
                                    ordering_title='total_partners', number=7,
                                    active=True, editable=True, category_id=partnership_summary.id),
        Partnership_summary_columns(title='active_partners', verbose_title='Активных партнеров',
                                    ordering_title='active_partners', number=8,
                                    active=True, editable=True, category_id=partnership_summary.id),
        Partnership_summary_columns(title='not_active_partners', verbose_title='Неактивных партнеров',
                                    ordering_title='not_active_partners', number=9,
                                    active=True, editable=True, category_id=partnership_summary.id),
    ])


def delete_partnership_summary_columns(apps, schema_editor):
    Partnership_summary_columns = apps.get_model("navigation", "ColumnType")
    Category = apps.get_model("navigation", "Category")

    Partnership_summary_columns.objects.filter(category__title='partnership_summary').delete()
    Category.objects.filter(title="partnership_summary").delete()


class Migration(migrations.Migration):
    dependencies = [
        ('navigation', '0020_auto_20170830_1258'),
    ]

    operations = [
        migrations.RunPython(create_partnership_summary_columns, delete_partnership_summary_columns)
    ]
