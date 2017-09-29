# -*- coding: utf-8
from __future__ import unicode_literals
from edem.settings.celery import app
from django.conf import settings
from datetime import datetime
import redis
from channels import Group
from json import dumps
import os


@app.task(ignore_result=True, max_retries=3, defailt_retry_delay=2 * 60)
def generate_export(user, queryset, fields, resource_class, file_format):
    data = resource_class().export(queryset, custom_export_fields=fields)
    export_data = file_format.export_data(data, delimiter=';')
    file_name = str(resource_class._meta.model.__name__) + '_export_at_' + datetime.now().strftime('%H:%M:%S')
    file_name_with_format = file_name + '.' + file_format.get_extension()

    path_to_file = settings.MEDIA_ROOT + '/exports/' + file_name_with_format

    result = bytes(export_data, 'UTF-8')

    os.makedirs(os.path.dirname(path_to_file), exist_ok=True)

    with open(path_to_file, 'wb') as file:
        file.write(result)

    url = settings.MEDIA_URL + 'exports/%s' % file_name_with_format

    try:
        r = redis.StrictRedis(host='redis', port=6379, db=0)
        r.sadd('export:{}'.format(user.id), url)
        r.expire('export:{}'.format(user.id), 24 * 60 * 60)
    except Exception as err:
        print(err)

    Group('export_{}'.format(user.id)).send({
        'text': dumps({'link': url, 'type': 'EXPORT', 'name': file_name})
    })
