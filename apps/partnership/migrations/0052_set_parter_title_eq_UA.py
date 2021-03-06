# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-27 10:51
from __future__ import unicode_literals

from django.db import migrations


def set_partner_title(apps, schema_editor):
    Partnership = apps.get_model("partnership", "Partnership")
    PartnershipLogs = apps.get_model("partnership", "PartnershipLogs")

    Partnership.objects.update(title='UA')
    PartnershipLogs.objects.update(title='UA')


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0051_auto_20171027_1050'),
    ]

    operations = [
        migrations.RunPython(set_partner_title),
    ]
