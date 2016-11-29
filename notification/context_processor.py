from django.utils import timezone

from notification.models import Notification


def notifications(request):
    date = timezone.now().date()

    return {'notifications': Notification.objects.filter(date=date)}
