# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-18 08:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0028_auto_20170216_1738'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='churchreport',
            options={'ordering': ('-date', 'church'), 'verbose_name': 'Church Report', 'verbose_name_plural': 'Church Reports'},
        ),
        migrations.AlterModelOptions(
            name='meeting',
            options={'ordering': ('-id', '-date'), 'verbose_name': 'Meeting', 'verbose_name_plural': 'Meetings'},
        ),
        migrations.AddField(
            model_name='meeting',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'in_progress'), (2, 'submitted'), (3, 'expired')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='count_repentance',
            field=models.IntegerField(default=0, verbose_name='Number of Repentance'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='currency_donations',
            field=models.CharField(blank=True, max_length=150, verbose_name='Donations in Currency'),
        ),
        migrations.AlterField(
            model_name='churchreport',
            name='new_people',
            field=models.IntegerField(default=0, verbose_name='New People'),
        ),
    ]