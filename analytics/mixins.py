from analytics.decorators import log_perform_update, log_perform_destroy, log_perform_create
from analytics.utils import model_to_dict, get_reverse_fields


class LogAndUpdateMixin(object):
    def log_and_update_obj(self, serializer):
        """
        instance -- the object which is saved.
        dict_with_changes -- dict with the object changes.

        Method for the saving object and creating ``dict``
        with state of the ``instance``. ``dict`` does not include
        new value of the ``reverse`` fields of the ``instance``.

        ``dict_with_changes`` format:
            dict_with_changes = dict(
                old=model_dict,
                new=model_dict,
            )

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

        =============================================================================
        # Method used in the ``analytics.decorators.log_perform_update`` decorator. #
        =============================================================================

        -------------------------------------------------------------------------------------------------
        class SomeUpdateView(UpdateModelMixin, LogAndUpdateMixin, ...):
            @log_perform_update
            def perform_update(self, serializer, **kwargs):
                new_object = kwargs.get('new_obj', None)
                dict_with_changes = kwargs.get('changes_dict', None)
                # some actions with ``new_object`` or ``dict_with_changes``
        -------------------------------------------------------------------------------------------------

        :param serializer:
        :return: instance, dict_with_changes = dict(old=dict(), new=dict())
        """
        cls = self.get_queryset().model
        fields = cls.get_tracking_fields()
        if len(fields) == 0:
            return serializer.save(), {}

        old_obj = self.get_object()
        old_obj_dict = model_to_dict(old_obj, fields=fields)

        old_rev_fields = get_reverse_fields(cls, old_obj)
        old_obj_dict.update(old_rev_fields)

        new_obj = serializer.save()
        new_obj_dict = model_to_dict(new_obj, fields=fields)
        return new_obj, {'old': old_obj_dict, 'new': new_obj_dict}

    @log_perform_update
    def perform_update(self, serializer, **kwargs):
        pass


class LogAndCreateMixin(object):
    def log_and_create_obj(self, serializer):
        cls = self.get_queryset().model
        fields = cls.get_tracking_fields()
        if len(fields) == 0:
            return serializer.save(), {}

        new_obj = serializer.save()
        new_obj_dict = model_to_dict(new_obj, fields=fields)
        return new_obj, new_obj_dict

    @log_perform_create
    def perform_create(self, serializer, **kwargs):
        pass


class LogAndDestroyMixin(object):
    def log_deletion_obj(self, instance):
        cls = self.get_queryset().model
        fields = cls.get_tracking_fields()
        if len(fields) == 0:
            return instance, {}

        old_obj = self.get_object()
        old_obj_dict = model_to_dict(old_obj, fields=fields)

        old_rev_fields = get_reverse_fields(cls, old_obj)
        old_obj_dict.update(old_rev_fields)

        return instance, old_obj_dict

    @log_perform_destroy
    def perform_destroy(self, instance, **kwargs):
        instance.delete()


class LogAndCreateUpdateDestroyMixin(LogAndCreateMixin, LogAndUpdateMixin, LogAndDestroyMixin):
    pass
