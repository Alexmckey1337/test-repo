from functools import wraps

from django.utils.translation import ugettext

from account.signals import obj_edit, obj_add, obj_delete
from analytics.utils import model_to_dict, get_reverse_fields


def log_change_payment(fields):
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            old_dict = model_to_dict(self, fields=fields)

            method(self, *args, **kwargs)

            new_dict = model_to_dict(self, fields=fields)
            editor = kwargs.get('editor')
            payment = kwargs.get('payment')

            obj_edit.send(
                sender=self.__class__,
                new_obj=self,
                old_obj_dict=old_dict,
                new_obj_dict=new_dict,
                editor=editor,
                reason={
                    'text': ugettext('Update after change payment'),
                    'object': {'id': payment.id, 'name': str(payment)}}
            )

        return wrapper

    return decorator


def log_perform_update(perform_update):
    """
    Decorator for saving object and logging the changes about its.

    Before the ``perform_update`` method is applied, the object is saved and
    ``dict = {'old': dict(), 'new': dict()}`` is created with state of the ``object``. But ``dict`` does not include
    new value of the ``reverse`` fields of the ``object``.

    Then the method ``perform_update`` called with some actions, such as updating ``reverse`` objects.

    After the ``perform_update`` method updates the dict for the new state of the fields ``reverse``,
    and the record is changed to the database.

    For saving and logging used method ``LogAndUpdateMixin.log_and_update_obj``

    -------------------------------------------------------------------------------------------------
    class SomeUpdateView(UpdateModelMixin, LogAndUpdateMixin, ...):
        @log_perform_update(self, serializer, **kwargs):
            new_object = kwargs.get('new_obj', None)
            dict_with_changes = kwargs.get('changes_dict', None)
            # some actions with new_object or dict_with_changes
    -------------------------------------------------------------------------------------------------

    :param perform_update: ``rest_framework.mixins.UpdateModelMixin.perform_update`` method
    :return:
    """

    @wraps(perform_update)
    def wrapper(self, serializer):
        new_obj, changes_dict = self.log_and_update_obj(serializer)

        instance = perform_update(self, serializer, new_obj=new_obj, changes_dict=changes_dict)

        if changes_dict:
            new_rev_fields = get_reverse_fields(new_obj._meta.model, new_obj)
            changes_dict['new'].update(new_rev_fields)

            obj_edit.send(
                sender=self.__class__,
                new_obj=new_obj,
                old_obj_dict=changes_dict['old'],
                new_obj_dict=changes_dict['new'],
                editor=getattr(self.request, 'real_user', self.request.user)
            )
        return instance

    return wrapper


def log_perform_create(perform_create):
    @wraps(perform_create)
    def wrapper(self, serializer):
        new_obj, addition_dict = self.log_and_create_obj(serializer)

        instance = perform_create(self, serializer, new_obj=new_obj, addition_dict=addition_dict)

        if addition_dict:
            new_rev_fields = get_reverse_fields(new_obj._meta.model, new_obj)
            addition_dict.update(new_rev_fields)

            obj_add.send(
                sender=self.__class__,
                obj=new_obj,
                obj_dict=addition_dict,
                editor=getattr(self.request, 'real_user', self.request.user)
            )
        return instance

    return wrapper


def log_perform_destroy(perform_destroy):
    @wraps(perform_destroy)
    def wrapper(self, instance):
        deletion_obj, deletion_dict = self.log_deletion_obj(instance)

        if deletion_dict:
            obj_delete.send(
                sender=self.__class__,
                obj=deletion_obj,
                obj_dict=deletion_dict,
                editor=getattr(self.request, 'real_user', self.request.user)
            )

        perform_destroy(self, instance, new_obj=deletion_obj, changes_dict=deletion_dict)

    return wrapper
