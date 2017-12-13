from django import template
from django.core.exceptions import ObjectDoesNotExist

from apps.account.models import CustomUser

register = template.Library()


@register.simple_tag(takes_context=True)
def user_can_edit(context, user_to_id, user_from=None):
    request = context['request']
    if user_from is None:
        user_from = request.user
    elif isinstance(user_from, (int, str)):
        try:
            user_from = CustomUser.objects.get(pk=user_from)
        except ObjectDoesNotExist:
            return False
    elif isinstance(user_from, CustomUser):
        pass
    else:
        return False

    if user_from.is_staff or user_from.id == user_to_id:
        return True
    if not user_from.hierarchy:
        return False
    if user_from.hierarchy.level < 2:
        return user_from.get_descendants().filter(pk=user_to_id).exists()
    return True