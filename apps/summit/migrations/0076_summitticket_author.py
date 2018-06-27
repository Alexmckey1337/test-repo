# Generated by Django 2.0.6 on 2018-06-27 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0045_customuser_is_proposal_manager'),
        ('summit', '0075_summit_one_entry'),
    ]

    operations = [
        migrations.AddField(
            model_name='summitticket',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_tickets', to='account.CustomUser', verbose_name='Author'),
        ),
    ]
