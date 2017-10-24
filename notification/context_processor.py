from datetime import datetime

from django.utils import timezone

from notification.backend import RedisBackend
from notification.models import Notification
from summit.models import SummitTicket, SummitAnket


def notifications(request):
    date = timezone.now().date()
    birthdays = Notification.objects.filter(date=date)

    try:
        r = RedisBackend()
        ticket_ids = r.smembers('summit:ticket:{}'.format(request.user.id))
        profile_email_error_ids = r.smembers('summit:email:code:error:{}'.format(request.user.id))
        profile_email_error_ids = sorted(
            list(map(lambda p: p.decode('utf8').split(':'), profile_email_error_ids)),
            key=lambda p: p[1])
        tickets = SummitTicket.objects.filter(id__in=ticket_ids)
        profiles = [(SummitAnket.objects.get(id=p[0]), datetime.fromtimestamp(int(p[1])).strftime('%d.%m.%Y %H:%M'))
                    for p in profile_email_error_ids]
        exports_count = len(r.smembers('export:%s' % request.user.id))

    except Exception as err:
        print(err)
        tickets = SummitTicket.objects.none()
        profiles = []
        exports_count = 0

    n = {
        'birthdays': birthdays,
        'summit_tickets': tickets,
        'profiles': profiles,
        'exports_count': exports_count,
        'count': birthdays.count() + tickets.count() + exports_count + len(profiles)
    }

    return {'notifications': n}
