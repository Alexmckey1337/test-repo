# Generated by Django 2.0.2 on 2018-03-04 04:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('partnership', '0055_auto_20180202_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='churchdeal',
            name='date_created',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='churchdeal',
            name='done',
            field=models.BooleanField(default=False, help_text='Deal is done?'),
        ),
        migrations.AlterField(
            model_name='churchdeal',
            name='partnership',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deals', to='partnership.ChurchPartner'),
        ),
        migrations.AlterField(
            model_name='churchdeal',
            name='responsible',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partner_disciples_deals', to='account.CustomUser', verbose_name='Responsible of partner'),
        ),
        migrations.AlterField(
            model_name='churchpartner',
            name='church',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='partners', to='group.Church'),
        ),
        migrations.AlterField(
            model_name='churchpartner',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='churchpartnerlog',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='deal',
            name='date_created',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='done',
            field=models.BooleanField(default=False, help_text='Deal is done?'),
        ),
        migrations.AlterField(
            model_name='partnership',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='partnershiplogs',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]