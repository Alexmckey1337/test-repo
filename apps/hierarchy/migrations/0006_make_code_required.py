# Generated by Django 2.0.4 on 2018-04-12 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0005_set_codes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hierarchy',
            name='code',
            field=models.SlugField(unique=True, verbose_name='Code'),
        ),
    ]