# Generated by Django 2.0.8 on 2018-09-05 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0076_summitticket_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='summitanket',
            name='device_code',
            field=models.CharField(blank=True, db_index=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='summitanket',
            name='first_name',
            field=models.CharField(blank=True, db_index=True, editable=False, max_length=255, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='summitattend',
            name='anket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attends', to='summit.SummitAnket', verbose_name='Anket'),
        ),
    ]