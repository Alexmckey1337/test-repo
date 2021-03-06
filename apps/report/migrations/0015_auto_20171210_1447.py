# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-10 14:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0014_auto_20160921_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthreport',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='month_reports', to='report.UserReport'),
        ),
        migrations.AlterField(
            model_name='userreport',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_report', to='account.CustomUser'),
        ),
        migrations.AlterField(
            model_name='weekreport',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='week_reports', to='report.UserReport'),
        ),
        migrations.AlterField(
            model_name='weekreport',
            name='week',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='week_reports', to='event.Week'),
        ),
        migrations.AlterField(
            model_name='yearreport',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='year_reports', to='report.UserReport'),
        ),
    ]
