# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2016-12-08 12:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('summit', '0031_anketemail_error_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='anketemail',
            name='is_success',
            field=models.BooleanField(default=True, verbose_name='Is success'),
        ),
    ]