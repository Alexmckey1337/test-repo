from rest_framework import serializers
from rest_framework.fields import get_attribute, empty, SkipField


class ReadOnlyChoiceField(serializers.ChoiceField):

    def to_representation(self, value):
        if value in ('', None):
            return value
        t = self.grouped_choices.get(value, value)
        return t


class DecimalWithCurrencyField(serializers.DecimalField):
    def __init__(self, *args, **kwargs):
        self.currency_field = kwargs.pop('currency_field', 'currency')
        super(DecimalWithCurrencyField, self).__init__(*args, **kwargs)

    def get_attribute(self, instance):
        attr = super(DecimalWithCurrencyField, self).get_attribute(instance)
        currency_format = getattr(instance, self.currency_field).output_format
        currency_dict = getattr(instance, self.currency_field).output_dict()

        return attr, currency_format, currency_dict

    def to_representation(self, value):
        value, currency_format, currency_dict = value
        value = super(DecimalWithCurrencyField, self).to_representation(value)
        currency_dict['value'] = value

        return currency_format.format(**currency_dict)


class ListCharField(serializers.ReadOnlyField):
    def __init__(self, **kwargs):
        self.fields = [f.split('.') for f in kwargs.pop('fields', [])]
        super(ListCharField, self).__init__(**kwargs)

    def get_attribute(self, instance):
        try:
            return [get_attribute(instance, f) for f in self.fields]
        except (KeyError, AttributeError) as exc:
            if not self.required and self.default is empty:
                raise SkipField()
            msg = (
                'Got {exc_type} when attempting to get a value for field '
                '`{field}` on serializer `{serializer}`.\nThe serializer '
                'field might be named incorrectly and not match '
                'any attribute or key on the `{instance}` instance.\n'
                'Original exception text was: {exc}.'.format(
                    exc_type=type(exc).__name__,
                    field=self.field_name,
                    serializer=self.parent.__class__.__name__,
                    instance=instance.__class__.__name__,
                    exc=exc
                )
            )
            raise type(exc)(msg)
