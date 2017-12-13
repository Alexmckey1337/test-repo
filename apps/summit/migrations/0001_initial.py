# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-29 13:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Summit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
            ],
        ),
        migrations.CreateModel(
            name='SummitAnket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.PositiveSmallIntegerField(default=0)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('summit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ankets', to='summit.Summit', verbose_name='\u0421\u0430\u043c\u043c\u0438\u0442')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summit_ankets', to='account.CustomUser')),
            ],
        ),
        migrations.CreateModel(
            name='SummitType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u0430\u043c\u043c\u0438\u0442\u0430')),
                ('image', models.ImageField(blank=True, null=True, upload_to='summit_type/images/')),
            ],
        ),
        migrations.AddField(
            model_name='summit',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='summits', to='summit.SummitType'),
        ),
        migrations.AlterUniqueTogether(
            name='summitanket',
            unique_together=set([('user', 'summit')]),
        ),
    ]