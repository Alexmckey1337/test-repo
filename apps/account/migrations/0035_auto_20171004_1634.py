# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-04 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0034_auto_20170925_1314'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMarker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('color', models.CharField(max_length=255, verbose_name='Color')),
                ('description', models.TextField(verbose_name='Description')),
            ],
            options={
                'verbose_name_plural': 'User Markers',
                'verbose_name': 'User Marker',
            },
        ),
        migrations.AddField(
            model_name='customuser',
            name='marker',
            field=models.ManyToManyField(blank=True, related_name='users', to='account.UserMarker', verbose_name='User Marker'),
        ),
    ]
