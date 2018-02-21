# Generated by Django 2.0.2 on 2018-02-20 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0017_auto_20180201_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='church',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Широта'),
        ),
        migrations.AddField(
            model_name='church',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Долгота'),
        ),
        migrations.AddField(
            model_name='homegroup',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Широта'),
        ),
        migrations.AddField(
            model_name='homegroup',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Долгота'),
        ),
        migrations.AlterField(
            model_name='church',
            name='city',
            field=models.CharField(blank=True, max_length=50, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='church',
            name='country',
            field=models.CharField(blank=True, max_length=50, verbose_name='Страна'),
        ),
        migrations.AlterField(
            model_name='homegroup',
            name='city',
            field=models.CharField(blank=True, max_length=50, verbose_name='Город'),
        ),
    ]
