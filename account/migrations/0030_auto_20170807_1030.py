# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-07 10:30
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0029_auto_20170713_1530'),
    ]

    operations = [
        TrigramExtension(),
    ]
