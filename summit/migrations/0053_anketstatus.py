# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-09 14:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0052_auto_20170606_1234'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnketStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg_code_requested', models.BooleanField(default=False, verbose_name='Запрос регистрационного кода')),
                ('active', models.BooleanField(default=True, verbose_name='Активна')),
                ('anket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='summit.SummitAnket', verbose_name='Anket')),
            ],
            options={
                'verbose_name': 'Статус Анкеты',
                'verbose_name_plural': 'Статусы Анкет',
            },
        ),
    ]
