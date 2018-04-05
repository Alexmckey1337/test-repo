from django.utils import timezone

from apps.account.models import CustomUser as User
from apps.notification.models import Notification


def create_notifications():
    date = timezone.now().date()
    user = User.objects.filter(born_date=date).first()
    if user:
        description = "Сегодня у %s День Рождения. Не забудьте поздравить коллегу." % (user.fullname)
        Notification.objects.create(theme="День рождения",
                                    description=description,
                                    common=True)


def sync_birthday():
    theme = "День Рождения"

    users = User.objects.filter(hierarchy__level__gte=2).all()
    for user in users:
        description = "Сегодня День Рождения отмечает %s! " % user.get_full_name()
        if user.born_date:
            day = user.born_date.weekday() + 1
            Notification.objects.get_or_create(
                user=user, theme=theme, defaults={
                    'description': description,
                    'date': user.born_date,
                    'day': day,
                    'common': True
                })
