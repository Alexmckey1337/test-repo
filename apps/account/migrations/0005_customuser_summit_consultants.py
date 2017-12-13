# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-24 12:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0017_auto_20161024_1511'),
        ('account', '0004_auto_20160922_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='summit_consultants',
            field=models.ManyToManyField(related_name='users', through='summit.SummitUserConsultant',
                                         to='summit.SummitType'),
        ),
    ]