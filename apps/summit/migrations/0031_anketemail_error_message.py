# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2016-12-08 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('summit', '0030_summit_mail_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='anketemail',
            name='error_message',
            field=models.TextField(blank=True, verbose_name='Error message'),
        ),
    ]