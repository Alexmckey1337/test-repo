from rest_framework import serializers


class ReadOnlyChoiceField(serializers.ChoiceField):

    def to_representation(self, value):
        if value in ('', None):
            return value
        t = self.grouped_choices.get(value, value)
        return t
