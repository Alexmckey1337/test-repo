# Generated by Django 2.0.2 on 2018-02-06 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0043_customuser_locality'),
        ('summit', '0069_auto_20180201_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='summitanket',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='regs', to='account.CustomUser', verbose_name='Author'),
        ),
    ]