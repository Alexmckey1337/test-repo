from django.utils import timezone


def today():
    return timezone.now().date()
