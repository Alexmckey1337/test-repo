import redis

from django.utils import timezone

from notification.models import Notification
from summit.models import SummitTicket


def notifications(request):
    date = timezone.now().date()
    birthdays = Notification.objects.filter(date=date)

    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        ticket_ids = r.smembers('summit:ticket:{}'.format(request.user.id))
        tickets = SummitTicket.objects.filter(id__in=ticket_ids)
    except Exception as err:
        tickets = SummitTicket.objects.none()
        print(err)

    n = {
        'birthdays': birthdays,
        'summit_tickets': tickets,
        'count': birthdays.count() + tickets.count()
    }
    return {'notifications': n}
