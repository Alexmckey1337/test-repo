# -*- coding: utf-8
from __future__ import unicode_literals
from edem.settings.celery import app
from django.conf import settings
from datetime import datetime
from channels import Group
from json import dumps
import os
import shutil

from notification.backend import RedisBackend


@app.task(ignore_result=True, max_retries=3, default_retra=2 * 60)
def generate_export(user, model, ids, fields, resource_class, file_format, file_name):
    data = resource_class().export(model.objects.filter(id__in=ids), custom_export_fields=fields)
    export_data = file_format.export_data(data, delimiter=';')
    file_name = file_name.replace(' ', '_') + '_export_at_' + datetime.now().strftime('%H:%M:%S')
    file_name_with_format = file_name + '.' + file_format.get_extension()

    path_to_file = settings.MEDIA_ROOT + '/exports/' + file_name_with_format

    result = export_data.encode('cp1251', errors='replace')

    os.makedirs(os.path.dirname(path_to_file), exist_ok=True)

    with open(path_to_file, 'wb') as file:
        file.write(result)

    url = settings.MEDIA_URL + 'exports/%s' % file_name_with_format

    try:
        r = RedisBackend()
        r.sadd('export:{}'.format(user), url)
        r.expire('export:{}'.format(user), 24 * 60 * 60)
    except Exception as err:
        print(err)

    Group('export_{}'.format(user)).send({
        'text': dumps({'link': url, 'type': 'EXPORT', 'name': file_name})
    })


@app.task(name='delete_expired_export', ignore_result=True, max_retries=5, default_retry_delay=10 * 60)
def delete_expired_export():
    try:
        r = RedisBackend()
        for user_exports in r.scan_iter('export:*'):
            r.delete(user_exports)

        shutil.rmtree(settings.MEDIA_ROOT + '/export/')

    except Exception as err:
        print(err)
