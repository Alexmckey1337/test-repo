from django import template
from django.conf import settings

from apps.account.models import CustomUser

register = template.Library()


@register.simple_tag()
def get_simple_managers():
    managers = CustomUser.objects.filter(
        partner_role__level__lte=settings.PARTNER_LEVELS['manager']).order_by(
        'last_name', 'first_name')
    return managers
