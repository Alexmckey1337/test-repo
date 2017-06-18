from datetime import datetime, timedelta

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from summit.models import SummitAnket, SummitAttend


class Command(BaseCommand):
    def handle(self, *args, **options):
        url = 'https://armspalace.esport.in.ua/m-ticket/gatelog/getLogs/'
        date_to = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_from = (datetime.now() - timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S')
        data = requests.get(url + '?dateFrom=' + date_from + '&dateTo=' + date_to)

        for _pass in data.json():
            date_time = datetime.strptime(_pass['date'], '%Y-%m-%d %H:%M:%S')
            try:
                anket = SummitAnket.objects.get(code=_pass['barcode'][4:])
            except ObjectDoesNotExist:
                continue
            SummitAttend.objects.get_or_create(
                anket=anket, date=date_time.date(), defaults={'time': date_time.time(),
                                                              'status': _pass['status']})
        ankets = SummitAnket.objects.all()

        summit_id = options.get('summit_id')
        if summit_id:
            ankets = ankets.filter(summit_id=summit_id)

        for anket in ankets:
            anket.update_value()
        self.stdout.write(
            'Successfully updated %s ankets\n' % ankets.count())
