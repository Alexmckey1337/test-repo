import logging
import os
import tempfile
from time import sleep

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from video_encoding.backends import get_backend
from video_encoding.exceptions import VideoEncodingError
from video_encoding.fields import VideoField
from video_encoding.models import Format

from edem.settings.celery import app

logger = logging.getLogger('tasks')

encoding_backend = get_backend()


@app.task(name='resize_all_video', ignore_result=True)
def resize_all_videos(app_label, model_name, pk):
    try_limit = 5
    model = apps.get_model(app_label=app_label, model_name=model_name)
    instance = None

    for i in range(try_limit):
        try:
            instance = model.objects.get(pk=pk)
        except ObjectDoesNotExist:
            sleep(5)
        else:
            break
    if instance is None:
        instance = model.objects.get(pk=pk)

    fields = instance._meta.fields
    for field in fields:
        if isinstance(field, VideoField):
            if not getattr(instance, field.name):
                # ignore empty fields
                continue

            # trigger conversion
            resize(getattr(instance, field.name))


def resize(fieldfile):
    instance = fieldfile.instance

    try:
        source_path = fieldfile.path
    except NotImplementedError:
        source_path = fieldfile.url

    object_id = instance.pk
    content_type = ContentType.objects.get_for_model(instance)

    for options in settings.VIDEO_ENCODING_FORMATS[encoding_backend.name]:
        resize_video.apply_async(args=[object_id, content_type.id, source_path, options, fieldfile.field.name, False])


@app.task(name='resize_video', ignore_result=True)
def resize_video(object_id, content_type_id, source_path, options, field_name, force=False):
    filename = os.path.basename(source_path)
    video_format, created = Format.objects.get_or_create(
        object_id=object_id,
        content_type_id=content_type_id,
        field_name=field_name, format=options['name'])

    # do not reencode if not requested
    if video_format.file and not force:
        return
    else:
        # set progress to 0
        video_format.reset_progress()

    # TODO do not upscale videos

    _, target_path = tempfile.mkstemp(
        suffix='_{name}.{extension}'.format(**options))

    try:
        encoding = encoding_backend.encode(
            source_path, target_path, options['params'])
        while encoding:
            try:
                progress = next(encoding)
            except StopIteration:
                break
            video_format.update_progress(progress)
    except VideoEncodingError:
        # TODO handle with more care
        video_format.delete()
        os.remove(target_path)
        return

        # save encoded file
    video_format.file.save('{filename}_{name}.{extension}'.format(filename=filename, **options),
                           File(open(target_path, mode='rb')))

    video_format.update_progress(100)  # now we are ready

    # remove temporary file
    os.remove(target_path)
