from django import template

from partnership.models import Partnership

register = template.Library()


@register.simple_tag()
def get_simple_managers():
    managers = Partnership.objects.filter(level__lte=Partnership.MANAGER).select_related('user').order_by(
        'user__last_name', 'user__first_name')
    return managers
