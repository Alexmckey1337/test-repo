# Generated by Django 2.0.8 on 2018-09-07 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0077_auto_20180905_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summitanket',
            name='device_code',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True),
        ),
    ]
