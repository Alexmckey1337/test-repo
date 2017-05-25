from django import template

from hierarchy.models import Department
from hierarchy.models import Hierarchy
from location.models import Country
from partnership.models import Partnership
from payment.models import Currency
from status.models import Division
from summit.models import SummitAnket, SummitUserConsultant, Summit
from account.models import CustomUser

register = template.Library()


@register.inclusion_tag('partials/create_user.html')
def create_user_form():
    managers = Partnership.objects.filter(
        level__lte=Partnership.MANAGER).select_related('user')
    countries = Country.objects.all()
    departments = Department.objects.all()
    hierarchies = Hierarchy.objects.all()
    divisions = Division.objects.all()
    currencies = Currency.objects.all()
    levels = CustomUser.SPIRITUAL_LEVEL_CHOICES

    ctx = {
        'managers': managers,
        'countries': countries,
        'departments': departments,
        'hierarchies': hierarchies,
        'divisions': divisions,
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
        user_from_anket.exists() and SummitUserConsultant.objects.filter(
            consultant=user_from_anket, user__user=user_to, summit=summit).exists())

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
