from django import template

from hierarchy.models import Department
from hierarchy.models import Hierarchy
from location.models import Country
from partnership.models import Partnership
from status.models import Division

register = template.Library()


@register.inclusion_tag('partials/create_user_summit.html')
def create_user_form():
    managers = Partnership.objects.filter(
        level__lte=Partnership.MANAGER).select_related('user')
    countries = Country.objects.all()
    departments = Department.objects.all()
    hierarchies = Hierarchy.objects.all()
    divisions = Division.objects.all()

    ctx = {
        'managers': managers,
        'countries': countries,
        'departments': departments,
        'hierarchies': hierarchies,
        'divisions': divisions,
    }
    return ctx
