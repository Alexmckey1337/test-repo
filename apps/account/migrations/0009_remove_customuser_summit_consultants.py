# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-17 09:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0008_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='summit_consultants',
        ),
    ]
