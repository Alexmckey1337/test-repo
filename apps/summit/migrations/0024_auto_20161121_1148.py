# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-21 09:48
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('summit', '0023_auto_20161117_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnketEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.CharField(max_length=255, verbose_name='Email')),
                ('subject', models.CharField(blank=True, max_length=255, verbose_name='Subject')),
                ('text', models.TextField(blank=True, verbose_name='Text')),
                ('html', models.TextField(blank=True, verbose_name='HTML text')),
                ('attach', models.FileField(blank=True, null=True, upload_to='tickets', verbose_name='Attach')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('anket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails',
                                            to='summit.SummitAnket', verbose_name='Anket')),
            ],
            options={
                'verbose_name': 'Anket email',
                'ordering': ('-created_at', 'anket'),
                'verbose_name_plural': 'Anket emails',
            },
        ),
    ]
