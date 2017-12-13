# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-29 13:45
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('hierarchy', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('middle_name', models.CharField(blank=True, default='', max_length=40)),
                ('phone_number', models.CharField(blank=True, default='', max_length=13, null=True)),
                ('skype', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('country', models.CharField(blank=True, default='', max_length=50)),
                ('region', models.CharField(blank=True, default='', max_length=50)),
                ('city', models.CharField(blank=True, default='', max_length=50)),
                ('district', models.CharField(blank=True, default='', max_length=50)),
                ('address', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('born_date', models.DateField(blank=True, null=True)),
                ('facebook', models.URLField(blank=True, default='', null=True)),
                ('vkontakte', models.URLField(blank=True, default='', null=True)),
                ('odnoklassniki', models.URLField(blank=True, default='', null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('description', models.TextField(blank=True, null=True)),
                ('repentance_date', models.DateField(blank=True, null=True)),
                ('coming_date', models.DateField(blank=True, null=True)),
                ('hierarchy_order', models.BigIntegerField(blank=True, null=True)),
                ('activation_key', models.CharField(blank=True, max_length=40)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='hierarchy.Department')),
                ('hierarchy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='hierarchy.Hierarchy')),
                ('master', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disciples', to='account.CustomUser')),
            ],
            options={
                'ordering': ['last_name'],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]