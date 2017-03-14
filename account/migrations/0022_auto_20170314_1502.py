# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-14 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0021_remove_customuser_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='departments',
            field=models.ManyToManyField(related_name='users', to='hierarchy.Department'),
        ),
    ]
