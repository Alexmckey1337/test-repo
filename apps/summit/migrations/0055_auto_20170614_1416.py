# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-14 14:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0054_auto_20170613_1726'),
    ]

    operations = [
        migrations.RunSQL('alter table summit_anketstatus alter reg_code_requested_date DROP NOT NULL;')
    ]
