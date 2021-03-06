# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-13 17:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0053_anketstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='anketstatus',
            name='reg_code_requested_date',
            field=models.DateTimeField(default=None, null=True, verbose_name='Дата ввода регистрационного кода'),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='ticket_status',
            field=models.CharField(choices=[('none', 'Without ticket.'), ('download', 'Ticket is created.'), ('print', 'Ticket is printed'), ('given', 'Ticket is given')], default='none', max_length=20, verbose_name='Ticket status'),
        ),
    ]
