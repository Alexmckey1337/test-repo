# Generated by Django 2.0.2 on 2018-02-26 12:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0070_summitanket_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_given', models.BooleanField(default=False, verbose_name='Билет выдан')),
                ('fullname', models.CharField(max_length=255, verbose_name='ФИО')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Номер Телефона')),
                ('secret', models.CharField(blank=True, max_length=10, null=True, verbose_name='Пароль пользователя')),
                ('amount', models.DecimalField(decimal_places=2, default=100, max_digits=10, verbose_name='Сумма оплаты')),
                ('currency', models.CharField(default='USD', max_length=5, verbose_name='Валюта оплаты')),
                ('paid', models.BooleanField(default=False, verbose_name='Статус оплаты')),
                ('liqpay_payment_id', models.IntegerField(blank=True, null=True, verbose_name='ID платежа в системе LiqPay')),
                ('liqpay_payment_token', models.CharField(blank=True, max_length=255, null=True, verbose_name='Токен платежа в системе LiqPay')),
                ('liqpay_payment_url', models.URLField(blank=True, null=True)),
                ('reg_date', models.DateField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('paid_date', models.DateField(blank=True, null=True, verbose_name='Дата оплаты')),
                ('chat_id', models.IntegerField(verbose_name='ID Telegram чата ')),
                ('summit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='telegram_payments', to='summit.Summit', verbose_name='Событие')),
            ],
            options={
                'verbose_name': 'Регистрация через Telegram Bot',
                'verbose_name_plural': 'Регистрации через Telegram Bot',
                'ordering': ('-id',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='telegrampayment',
            unique_together={('id', 'phone_number')},
        ),
    ]
