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

