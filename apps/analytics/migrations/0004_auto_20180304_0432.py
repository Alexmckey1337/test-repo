# Generated by Django 2.0.2 on 2018-03-04 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_logrecord_raw_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logrecord',
            name='action_flag',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Добавление'), (2, 'Изминение'), (3, 'Удаление')], default=2, verbose_name='action flag'),
        ),
    ]
