# Generated by Django 2.0.6 on 2018-07-05 07:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0048_auto_20180705_0758'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightAuthUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='light_auth', to='account.CustomUser')),
            ],
        ),
        migrations.CreateModel(
            name='PhoneConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created')),
                ('sent', models.DateTimeField(null=True, verbose_name='sent')),
                ('key', models.CharField(max_length=64, unique=True, verbose_name='key')),
            ],
            options={
                'verbose_name': 'phone confirmation',
                'verbose_name_plural': 'phone confirmations',
            },
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=40, unique=True, verbose_name='phone number')),
                ('verified', models.BooleanField(default=False, verbose_name='verified')),
                ('primary', models.BooleanField(default=False, verbose_name='primary')),
                ('auth_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='light_auth.LightAuthUser', verbose_name='auth')),
            ],
            options={
                'verbose_name': 'phone number',
                'verbose_name_plural': 'phone numbers',
            },
        ),
        migrations.AddField(
            model_name='phoneconfirmation',
            name='phone_number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='light_auth.PhoneNumber', verbose_name='phone number'),
        ),
    ]