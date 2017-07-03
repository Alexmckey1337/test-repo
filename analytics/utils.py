from datetime import date, datetime
from decimal import Decimal
from itertools import chain

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import ManyToManyField
from django.db.models.fields.files import ImageFieldFile


def foreign_key_to_dict(instance=None, verbose: str = ''):
    return {
        'value': {
            'id': instance.id if instance else None,
            'name': str(instance)
        },
        'verbose_name': verbose
    }


def model_to_dict(instance, fields=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``model_dict`` format:

        model_dict = dict(
            simple_field = dict(value='value', verbose_name='Field name'),
            foreign_key_field = foreign_key_dict,
            generic_foreign_key_field = foreign_key_dict,
            m2m_field = m2m_dict,
        )

        foreign_key_dict = dict(
            value = dict(id=1, name=object_name),
            verbose_name='Field name'
        )

        m2m_dict = dict(
            value = [1, 4],
            verbose_name='Many to many field'
        )
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False) and not isinstance(f, GenericForeignKey):
            continue
        if fields and f.name not in fields:
            continue
        if isinstance(f, ManyToManyField):
            data[f.name] = {'value': f.value_from_object(instance), 'verbose_name': str(f.verbose_name)}
        if isinstance(f, GenericForeignKey):
            obj_id = getattr(instance, f.fk_field)
            obj = getattr(instance, f.ct_field).model_class().objects.get(pk=obj_id)
            data[f.name] = {
                'value': {
                    'id': obj_id,
                    'name': str(obj)
                },
                'verbose_name': str(f.name)
            }
        elif f.is_relation:
            obj_id = f.value_from_object(instance)
            obj = f.remote_field.model.objects.get(pk=obj_id) if obj_id else ''
            data[f.name] = {
                'value': {
                    'id': obj_id,
                    'name': str(obj),
                },
                'verbose_name': str(f.verbose_name)}
        else:
            data[f.name] = {'value': f.value_from_object(instance), 'verbose_name': str(f.verbose_name)}
    return data


def get_field(value):
    if isinstance(value, (date, datetime)):
        return value.strftime('%d %B %Y')
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, ImageFieldFile):
        return value.name
    return value


def get_reverse_fields(cls, obj) -> dict:
    rev_fields = dict()
    for field in cls.get_tracking_reverse_fields():
        rev_fields[field] = {
            "value": list(getattr(obj, field).values_list('id', flat=True)),
            'verbose_name': field
        }
    return rev_fields
