# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-24 08:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0036_auto_20170106_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='summitanket',
            name='ticket_status',
            field=models.CharField(choices=[('none', 'Without ticket.'), ('download', 'Ticket is downloaded.'), ('print', 'Ticket is printed')], default='none', max_length=20, verbose_name='Ticket status'),
        ),
    ]
