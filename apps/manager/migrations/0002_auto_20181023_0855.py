# Generated by Django 2.0.8 on 2018-10-23 08:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0048_auto_20180705_0758'),
        ('group', '0027_auto_20181022_1431'),
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupsManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manage_person', to='group.HomeGroup', unique=True, verbose_name='Group')),
                ('person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_groups', to='account.CustomUser', verbose_name='Group manager')),
            ],
        ),
        migrations.RemoveField(
            model_name='manager',
            name='group',
        ),
        migrations.RemoveField(
            model_name='manager',
            name='person',
        ),
        migrations.DeleteModel(
            name='Manager',
        ),
    ]
