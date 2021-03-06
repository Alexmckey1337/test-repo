from django import template

from apps.account.models import CustomUser
from apps.payment.models import Currency
from apps.summit.models import SummitAnket, SummitUserConsultant, Summit

register = template.Library()


@register.inclusion_tag('partials/create_user.html', takes_context=True)
def create_user_form(context):
    request = context['request']
    currencies = Currency.objects.all()
    levels = CustomUser.SPIRITUAL_LEVEL_CHOICES

    ctx = {
        'request': request,
        'currencies': currencies,
        'spiritual_levels': [{'id': v[0], 'title': v[1]} for v in levels]
    }
    return ctx


@register.simple_tag(takes_context=True)
def is_consultant_for_user(context, summit, user_to, user_from=None):
    request = context['request']
    if user_from is None:
        user_from = request.user
    user_from_anket = SummitAnket.objects.filter(
        user=user_from, summit=summit, role__gte=SummitAnket.CONSULTANT)
    is_consultant = (
            user_from_anket.exists() and user_from_anket.count() == 1 and
            SummitUserConsultant.objects.filter(
                consultant=user_from_anket.get(), user__user=user_to, summit=summit).exists())

    return is_consultant


@register.simple_tag
def available_summits(user, summit_type=None):
    qs_filter = {
        'ankets__user': user,
        'ankets__role__gte': SummitAnket.CONSULTANT
    }
    if summit_type:
        return summit_type.summits.filter(**qs_filter).distinct()
    return Summit.objects.filter(**qs_filter).distinct()


@register.simple_tag
def is_summit_consultant_or_high(user, summit):
    return user.is_summit_consultant_or_high(summit)


@register.simple_tag
def is_summit_supervisor_or_high(user, summit):
    return user.is_summit_supervisor_or_high(summit)
