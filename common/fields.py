import json

from rest_framework import serializers
from rest_framework.fields import empty


class RequestQueryField(serializers.JSONField):
    """
    Field class for DRF serializer that sets the whole query
    passed to the parental serializer as a dict
    """
    def get_value(self, dictionary):
        # A hack to make it work in tests too.
        # Haven't found a better way
        if 'csrfmiddlewaretoken' in dictionary:
            value = super().get_value(dictionary)
        else:
            value = {}
            for key in dictionary:
                value[key] = dictionary.get(key, empty)
        return value


class TextInputListField(serializers.ListField):
    """
    ListField with text input in HTML forms
    """
    def __init__(self, *args, **kwargs):
        style = {'base_template': 'input.html'}
        super().__init__(*args, style=style, **kwargs)

    def get_value(self, dictionary):
        """
        A text input does not convert input string to list automatically,
        so we need to do it manually, first checking that this is a form
        """
        value = super().get_value(dictionary)
        is_querydict = hasattr(dictionary, 'getlist')  # DRF checks that the same way internally
        is_form = 'csrfmiddlewaretoken' in dictionary
        if value and is_querydict and is_form:
            try:
                value = json.loads(value[0])
            except Exception:
                pass
        return value


class MultipleChoiceListField(serializers.MultipleChoiceField):
    """
    MultipleChoiceField that returns list instead of set,
    which allows to automatically jsonify its value
    """
    def to_representation(self, value):
        value = super().to_representation(value)
        return list(value)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return list(value)
