# Generated by Django 2.0.2 on 2018-03-07 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0073_auto_20180304_0432'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegrampayment',
            name='err_description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Описание ошибки'),
        ),
    ]