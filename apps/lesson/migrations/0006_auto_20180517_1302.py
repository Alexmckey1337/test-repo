# Generated by Django 2.0.5 on 2018-05-17 13:02

import apps.lesson.validators
import common.video
from django.db import migrations, models
import django.db.models.deletion
import video_encoding.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0005_auto_20180504_0857'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('width', models.PositiveIntegerField(editable=False, null=True)),
                ('height', models.PositiveIntegerField(editable=False, null=True)),
                ('duration', models.FloatField(editable=False, null=True)),
                ('file', video_encoding.fields.VideoField(height_field='height', upload_to=common.video.video_directory_path, width_field='width')),
            ],
            options={
                'verbose_name': 'Video file',
                'verbose_name_plural': 'Video files',
                'db_table': 'lesson_video_file',
            },
        ),
        migrations.AlterField(
            model_name='videolesson',
            name='url',
            field=apps.lesson.validators.YoutubeURLField(blank=True, editable=False, max_length=255, verbose_name='youtube url'),
        ),
        migrations.AddField(
            model_name='videolesson',
            name='file',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lessons', to='lesson.VideoFile', verbose_name='Video file'),
        ),
    ]
