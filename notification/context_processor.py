import redis

from django.utils import timezone

from notification.models import Notification
from summit.models import SummitTicket


def notifications(request):
    date = timezone.now().date()
    birthdays = Notification.objects.filter(date=date)

    try:
        r = redis.StrictRedis(host='redis', port=6379, db=0)
        ticket_ids = r.smembers('summit:ticket:{}'.format(request.user.id))
        tickets = SummitTicket.objects.filter(id__in=ticket_ids)
        exports_count = len(r.smembers('export:%s' % request.user.id))

    except Exception as err:
        print(err)
        tickets = SummitTicket.objects.none()
        exports_count = 0

    n = {
        'birthdays': birthdays,
        'summit_tickets': tickets,
        'exports_count': exports_count,
        'count': birthdays.count() + tickets.count() + exports_count
    }
    print(n)
    return {'notifications': n}
