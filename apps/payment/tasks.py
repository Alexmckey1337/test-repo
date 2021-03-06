from importlib import import_module

from django.apps import apps
from django.core.files.storage import default_storage
import io
from django.utils import timezone
from import_export.formats.base_formats import CSV

from edem.settings.celery import app
from django.conf import settings
from channels import Group
from json import dumps
import shutil

from apps.notification.backend import RedisBackend
from apps.summit.models import SummitAnket


formats = {
    'text/csv': CSV
}


@app.task(max_retries=3, default_retry_delay=2 * 60)
def generate_export(user_id, app_label, model_name, ids, fields,
                    resource_module, resource_class_name, content_type, file_name):
    file_format = formats.get(content_type, CSV)()
    resource_class = getattr(import_module(resource_module), resource_class_name)
    model = apps.get_model(app_label=app_label, model_name=model_name)
    qs = model.objects.filter(id__in=ids)
    if model == SummitAnket:
        qs = qs.annotate_full_name()
    data = resource_class().export(qs, custom_export_fields=fields)
    export_data = file_format.export_data(data, delimiter=';')
    file_name = file_name.replace(' ', '_') + '_export_at_' + timezone.now().strftime('%H:%M:%S')
    file_name_with_format = file_name + '.' + file_format.get_extension()

    path_to_file = 'exports/' + file_name_with_format

    result = export_data.encode('cp1251', errors='replace')

    default_storage.save(path_to_file, io.BytesIO(result))

    url = settings.MEDIA_URL + 'exports/%s' % file_name_with_format

    try:
        r = RedisBackend()
        r.sadd('export:{}'.format(user_id), url)
        r.expire('export:{}'.format(user_id), 24 * 60 * 60)
    except Exception as err:
        print(err)

    Group('export_{}'.format(user_id)).send({
        'text': dumps({'link': url, 'type': 'EXPORT', 'name': file_name})
    })


@app.task(name='delete_expired_export', ignore_result=True, max_retries=5, default_retry_delay=10 * 60)
def delete_expired_export():
    try:
        r = RedisBackend()
        for user_exports in r.scan_iter('export:*'):
            r.delete(user_exports)

        shutil.rmtree(settings.MEDIA_ROOT + '/exports/')

    except Exception as err:
        print(err)
