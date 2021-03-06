# Generated by Django 2.0.6 on 2018-07-02 07:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0046_customuser_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessengerType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.SlugField(max_length=60, unique=True, verbose_name='Code')),
                ('title', models.CharField(max_length=60, unique=True, verbose_name='Title')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='messengers', verbose_name='Icon')),
                ('display_position', models.SmallIntegerField(default=0, verbose_name='Display Position')),
            ],
            options={
                'verbose_name': 'Messenger Type',
                'verbose_name_plural': 'Messenger Types',
                'db_table': 'account_messenger',
                'ordering': ('display_position',),
            },
        ),
        migrations.CreateModel(
            name='UserMessenger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=80, verbose_name='Value')),
                ('display_position', models.SmallIntegerField(default=0, verbose_name='Display Position')),
                ('messenger', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='account.MessengerType', verbose_name='Messenger')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messengers', to='account.CustomUser', verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Messenger',
                'verbose_name_plural': 'User Messengers',
                'db_table': 'account_user_messenger',
                'ordering': ('display_position', 'messenger__display_position'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='usermessenger',
            unique_together={('user', 'messenger')},
        ),
    ]
