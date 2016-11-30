from django import template

from partnership.models import Partnership

register = template.Library()


@register.simple_tag()
def get_simple_partners():
    partners = Partnership.objects.filter(level__lte=Partnership.MANAGER).select_related('user')
    return partners
