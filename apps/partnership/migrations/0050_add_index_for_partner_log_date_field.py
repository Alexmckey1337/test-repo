# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-23 16:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0035_auto_20171004_1634'),
        ('partnership', '0049_add_partner_title_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnerrolelog',
            name='log_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Log date'),
        ),
        migrations.AlterField(
            model_name='partnershiplogs',
            name='log_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Log date'),
        ),
        migrations.AlterUniqueTogether(
            name='partnership',
            unique_together=set([('user', 'title')]),
        ),
    ]
