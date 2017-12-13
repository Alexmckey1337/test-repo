# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-12 15:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0039_auto_20170512_1246'),
    ]

    operations = [
        migrations.CreateModel(
            name='SummitEventTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(verbose_name='Дата и Время')),
                ('name_ru', models.CharField(max_length=64, verbose_name='Название на Русском')),
                ('author_ru', models.CharField(max_length=64, verbose_name='Имя автора на Русском')),
                ('name_en', models.CharField(max_length=64, verbose_name='Название на Английском')),
                ('author_en', models.CharField(max_length=64, verbose_name='Имя автора на Английском')),
                ('name_de', models.CharField(max_length=64, verbose_name='Название на Немецком')),
                ('author_de', models.CharField(max_length=64, verbose_name='Имя автора на Немецком')),
                ('summit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='summit.Summit', verbose_name='Саммит')),
            ],
        ),
    ]