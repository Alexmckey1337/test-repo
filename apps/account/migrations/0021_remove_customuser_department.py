# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-10 13:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_auto_20170309_1744'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='department',
        ),
    ]
