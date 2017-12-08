from apps.account.models import CustomUser


def spiritual_levels(request):
    levels = CustomUser.SPIRITUAL_LEVEL_CHOICES
    return {'spiritual_levels': [{'id': v[0], 'title': v[1]} for v in levels]}
