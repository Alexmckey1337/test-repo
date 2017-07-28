import json

from django import template

register = template.Library()


@register.filter()
def js(value):
    return json.dumps(value)
