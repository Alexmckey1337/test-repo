# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-28 09:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0005_homegroup_active'),
        ('event', '0030_churchreport_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='churchreport',
            options={'ordering': ('-id', '-date'), 'verbose_name': 'Church Report', 'verbose_name_plural': 'Church Reports'},
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='count_people',
            field=models.IntegerField(default=0, verbose_name='Count People'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='donations',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='Donations'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='pastor_tithe',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='Pastor Tithe'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='tithe',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='Tithe'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='transfer_payments',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='Transfer Payments'),
        ),
        migrations.AlterField(
            model_name='meetingattend',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attends', to='event.Meeting', verbose_name='Meeting'),
        ),
        migrations.AlterField(
            model_name='meetingattend',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attends', to='account.CustomUser', verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='meetingtype',
            name='image',
            field=models.ImageField(blank=True, upload_to='images', verbose_name='Изображение'),
        ),
        migrations.AlterUniqueTogether(
            name='churchreport',
            unique_together=set([('church', 'date', 'status')]),
        ),
        migrations.AlterUniqueTogether(
            name='meeting',
            unique_together=set([('type', 'date', 'home_group')]),
        ),
    ]
