# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-28 12:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0036_auto_20170725_1731'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='churchreport',
            options={'ordering': ('-id', '-date'), 'verbose_name': 'Отчет церкви', 'verbose_name_plural': 'Отчеты церкви'},
        ),
        migrations.AlterModelOptions(
            name='meeting',
            options={'ordering': ('-id', '-date'), 'verbose_name': 'Встреча', 'verbose_name_plural': 'Встречи'},
        ),
        migrations.AlterModelOptions(
            name='meetingattend',
            options={'ordering': ('meeting__owner', '-meeting__date'), 'verbose_name': 'Meeting attend', 'verbose_name_plural': 'Участники встречи'},
        ),
        migrations.AlterModelOptions(
            name='meetingtype',
            options={'verbose_name': 'Тип встречи', 'verbose_name_plural': 'Тип встреч'},
        ),
        migrations.AddField(
            model_name='churchreport',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Comment'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='church',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='group.Church', verbose_name='Церковь'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='count_repentance',
            field=models.IntegerField(default=0, verbose_name='Количество покаяний'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='currency_donations',
            field=models.CharField(blank=True, max_length=150, verbose_name='Пожертвования в валюте'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='donations',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='Пожертвования'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='new_people',
            field=models.IntegerField(default=0, verbose_name='Новые люди'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'in_progress'), (2, 'отправлено'), (3, 'просроченный')], default=1, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='tithe',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='Десятина'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='home_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.HomeGroup', verbose_name='Домашняя группа'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'in_progress'), (2, 'отправлено'), (3, 'просроченный')], default=1, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='total_sum',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='Общая сумма'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.MeetingType', verbose_name='Тип встречи'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='visitors',
            field=models.ManyToManyField(related_name='meeting_types', through='event.MeetingAttend', to='account.CustomUser', verbose_name='Посетители'),
        ),
        migrations.AlterField(
            model_name='meetingattend',
            name='attended',
            field=models.BooleanField(default=False, verbose_name='Присутствовали'),
        ),
        migrations.AlterField(
            model_name='meetingattend',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attends', to='event.Meeting', verbose_name='Встреча'),
        ),
        migrations.AlterField(
            model_name='meetingattend',
            name='note',
            field=models.TextField(blank=True, verbose_name='Заметка'),
        ),
        migrations.AlterField(
            model_name='meetingtype',
            name='code',
            field=models.SlugField(max_length=255, unique=True, verbose_name='Код'),
        ),
        migrations.AlterField(
            model_name='meetingtype',
            name='image',
            field=models.ImageField(blank=True, upload_to='images', verbose_name='Фото'),
        ),
    ]