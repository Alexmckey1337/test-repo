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
        export_urls = r.smembers('export:%s' % request.user.id)
    except Exception as err:
        tickets = SummitTicket.objects.none()
        export_urls = []

    n = {
        'birthdays': birthdays,
        'summit_tickets': tickets,
        'export_urls': export_urls,
        'count': birthdays.count() + tickets.count() + len(export_urls)
    }
    return {'notifications': n}
