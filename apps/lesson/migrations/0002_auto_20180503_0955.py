# Generated by Django 2.0.5 on 2018-05-03 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='textlesson',
            name='access_level',
            field=models.IntegerField(choices=[(1, 'Leader+'), (2, 'Pastor+')], default=1, verbose_name='Access level'),
        ),
        migrations.AddField(
            model_name='videolesson',
            name='access_level',
            field=models.IntegerField(choices=[(1, 'Leader+'), (2, 'Pastor+')], default=1, verbose_name='Access level'),
        ),
    ]
