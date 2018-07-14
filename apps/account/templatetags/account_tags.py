from django import template
from django.core.exceptions import ObjectDoesNotExist

from apps.account.models import CustomUser, UserMessenger
from apps.light_auth.api.permissions import has_light_auth_perm as _has_light_auth_perm

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

    if user_from.is_staff or user_from.has_operator_perm or user_from.id == user_to_id:
        return True
    if not user_from.hierarchy:
        return False
    if user_from.hierarchy.level < 2:
        return user_from.get_descendants().filter(pk=user_to_id).exists()
    return True


@register.simple_tag(takes_context=True)
def has_light_auth_perm(context, user_to=None, user_from=None):
    request = context['request']
    if user_from is None:
        user_from = request.user

    return _has_light_auth_perm(user_from, user_to)


@register.simple_tag
def messenger(code, user):
    try:
        return UserMessenger.objects.get(user=user, messenger__code=code).value
    except UserMessenger.DoesNotExist:
        return ''
