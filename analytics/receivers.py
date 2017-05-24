from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.utils.translation import ugettext

from account.signals import obj_edit, obj_add, obj_delete
from analytics.models import LogRecord
from analytics.utils import get_field


@receiver(obj_edit)
def receive_obj_edit(sender, new_obj, old_obj_dict, new_obj_dict, editor, reason=ugettext('Edit object'), **kwargs):
    diff_dict = dict()
    for obj_field in old_obj_dict.keys():
        old_value = old_obj_dict[obj_field]['value']
        new_value = new_obj_dict[obj_field]['value']
        if old_value != new_value:
            diff_dict[obj_field] = {
                "value": {"old": get_field(old_value), "new": get_field(new_value)},
                "verbose_name": old_obj_dict[obj_field]['verbose_name']}
    if diff_dict:
        LogRecord.objects.create(
            user=editor,
            content_type=ContentType.objects.get_for_model(new_obj),
            object_id=new_obj.id,
            object_repr=str(new_obj),
            action_flag=LogRecord.CHANGE,
            change_data={
                "changed": diff_dict,
                "reason": reason
            }
        )


@receiver(obj_add)
def receive_obj_add(sender, obj, obj_dict, editor, reason=ugettext('Create object'), **kwargs):
    diff_dict = dict()
    for obj_field in obj_dict.keys():
        new_value = obj_dict[obj_field]['value']
        if new_value:
            diff_dict[obj_field] = {
                "value": get_field(new_value),
                "verbose_name": obj_dict[obj_field]['verbose_name']}
    if diff_dict:
        LogRecord.objects.create(
            user=editor,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            object_repr=str(obj),
            action_flag=LogRecord.ADDITION,
            change_data={
                "addition": diff_dict,
                "reason": reason
            }
        )


@receiver(obj_delete)
def receive_obj_del(sender, obj, obj_dict, editor, reason=ugettext('Delete object'), **kwargs):
    diff_dict = dict()
    for obj_field in obj_dict.keys():
        new_value = obj_dict[obj_field]['value']
        if new_value:
            diff_dict[obj_field] = {
                "value": get_field(new_value),
                "verbose_name": obj_dict[obj_field]['verbose_name']}
    if diff_dict:
        LogRecord.objects.create(
            user=editor,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            object_repr=str(obj),
            action_flag=LogRecord.DELETION,
            change_data={
                "deletion": diff_dict,
                "reason": reason
            }
        )
