# -*- coding: utf-8
from models import Notification
from django.utils import timezone
from datetime import timedelta
from account.models import CustomUser as User


def create_notifications():
    date = timezone.now().date()
    user = User.objects.filter(born_date=date).first()
    if user:
        description = "Сегодня у %s День Рождения. Не забудьте поздравить коллегу." % (user.fullname)
        notification = Notification.objects.create(theme="День рождения",
                                                   description=description,
                                                   common=True)


def sync_birthday():
    theme = u"День Рождения"

    users = User.objects.filter(hierarchy__level__gte=2).all()
    for user in users:
        description = u"Сегодня День Рождения отмечает %s! " % user.get_full_name()
        if user.born_date:
            day = user.born_date.weekday() + 1
            try:
                notification = Notification.objects.get(user=user,
                                                        theme=theme)
                pass
            except Notification.DoesNotExist:
                notification = Notification.objects.create(user=user,
                                                           theme=theme,
                                                           description=description,
                                                           date=user.born_date,
                                                           day=day,
                                                           common=True)



