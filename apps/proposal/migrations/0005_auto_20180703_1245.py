# Generated by Django 2.0.6 on 2018-07-03 12:45

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('summit', '0076_summitticket_author'),
        ('account', '0047_auto_20180702_0738'),
        ('proposal', '0004_proposal_raw_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(editable=False, max_length=25, verbose_name='Status')),
                ('note', models.TextField(verbose_name='Note')),
                ('closed_at', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Closed at')),
                ('reason', models.CharField(choices=[('create', 'Create'), ('update', 'Update')], editable=False, max_length=25, verbose_name='Reason')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created at')),
                ('manager', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='proposal_event_histories', to='account.CustomUser', verbose_name='Manager')),
                ('owner', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='owner_event_histories', to='account.CustomUser', verbose_name='Owner')),
                ('profile', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='summit.SummitAnket', verbose_name='Event profile')),
            ],
        ),
        migrations.CreateModel(
            name='EventProposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, verbose_name='raw data')),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In progress'), ('reopen', 'Reopen'), ('rejected', 'Rejected'), ('processed', 'Processed')], default='open', max_length=25, verbose_name='Status')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('closed_at', models.DateTimeField(blank=True, null=True, verbose_name='Closed at')),
                ('note', models.TextField(verbose_name='Note')),
                ('info', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, verbose_name='Additional information')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='manager_event_proposals', to='account.CustomUser', verbose_name='Manager')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='proposals', to='summit.SummitAnket', verbose_name='Event profile')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.CustomUser')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='eventhistory',
            name='proposal',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='histories', to='proposal.EventProposal', verbose_name='Event Proposal'),
        ),
    ]