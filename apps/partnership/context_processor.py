from django.conf import settings


def partner_levels(request):
    levels = settings.PARTNER_LEVELS
    return {'partner_levels': [{'id': v[1], 'title': v[0]} for v in levels.items()]}
