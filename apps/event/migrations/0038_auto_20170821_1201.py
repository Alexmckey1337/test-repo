# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-21 12:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import apps.payment.models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0011_payment_operation'),
        ('event', '0037_auto_20170728_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='churchreport',
            name='currency',
            field=models.ForeignKey(default=apps.payment.models.get_default_currency, null=True, on_delete=django.db.models.deletion.PROTECT, to='payment.Currency', verbose_name='Currency'),
        )
    ]