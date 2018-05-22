# Generated by Django 2.0.5 on 2018-05-22 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0020_auto_20180306_1434'),
    ]

    operations = [
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.SlugField(blank=True, editable=False, max_length=60, verbose_name='Код')),
                ('title', models.CharField(max_length=40, verbose_name='Заглавие')),
            ],
        ),
        migrations.AddField(
            model_name='homegroup',
            name='language',
            field=models.CharField(blank=True, choices=[('ua', 'Ukraine'), ('ru', 'Русский'), ('en', 'Английский'), ('de', 'Germany')], max_length=10, verbose_name='Language'),
        ),
        migrations.AddField(
            model_name='homegroup',
            name='directions',
            field=models.ManyToManyField(related_name='home_groups', to='group.Direction'),
        ),
    ]
