from os import path

from slugify import slugify


def video_directory_path(instance, filename):
    ext = ''
    if '.' in filename:
        filename, ext = path.splitext(filename)
    if hasattr(instance, 'video_path') and instance.video_path:
        video_path = instance.video_path
    else:
        video_path = instance.__class__.__name__.lower()

    if hasattr(instance, 'name') and instance.name:
        name = '{}_'.format(instance.name)
    elif hasattr(instance, 'title') and instance.title:
        name = '{}_'.format(instance.title)
    elif hasattr(instance, 'value') and instance.value:
        name = '{}_'.format(instance.value)
    else:
        name = '{}_'.format(instance.pk)
    return 'videos/{}/{}{}{}'.format(
        video_path, slugify(name), slugify(filename), ext)