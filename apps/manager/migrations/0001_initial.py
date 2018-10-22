# Generated by Django 2.0.8 on 2018-10-22 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0048_auto_20180705_0758'),
        ('group', '0027_auto_20181022_1431'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manage_person', to='group.HomeGroup', unique=True, verbose_name='Group')),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_groups', to='account.CustomUser', verbose_name='Manager')),
            ],
        ),
    ]
