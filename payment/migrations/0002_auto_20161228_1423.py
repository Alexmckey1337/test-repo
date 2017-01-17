# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2016-12-28 12:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ('-created_at',), 'verbose_name': 'Payment', 'verbose_name_plural': 'Payments'},
        ),
        migrations.AlterField(
            model_name='payment',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]