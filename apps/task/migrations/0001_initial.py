# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-30 14:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('status', '0001_initial'),
        ('account', '0036_customuser_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('in_work', 'in_work'), ('done', 'done')], default='in_work', max_length=255, verbose_name='Status')),
                ('date_published', models.DateField(verbose_name='Date Published')),
                ('description', models.TextField(verbose_name='Description')),
                ('date_finish', models.DateField(blank=True, verbose_name='Date Finish', null=True)),
                ('finish_report', models.TextField(blank=True, verbose_name='Finish Report', null=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_creator', to='account.CustomUser', verbose_name='Task Creator')),
                ('division', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='status.Division', verbose_name='Division')),
                ('executor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_executor', to='account.CustomUser', verbose_name='Task Executor')),
                ('target', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_target', to='account.CustomUser', verbose_name='Task Target')),
            ],
            options={
                'verbose_name_plural': 'User Tasks',
                'ordering': ['status', '-date_published'],
                'verbose_name': 'User Task',
            },
        ),
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='Title')),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='task.TaskType', verbose_name='TaskType'),
        ),
    ]
