from rest_framework import serializers


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
