# Generated by Django 2.0.6 on 2018-06-16 08:46

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0003_auto_20180614_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='raw_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, verbose_name='raw data'),
        ),
    ]