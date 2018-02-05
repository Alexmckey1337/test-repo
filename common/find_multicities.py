from collections import defaultdict

from django.db.models import Q

from apps.account.models import CustomUser
from apps.location.models import City


def d():
    cc = defaultdict(list)
    for u in CustomUser.objects.filter(
            locality__isnull=True).exclude(
            Q(city='') | Q(city=' ')).values('pk', 'country', 'city', 'region'):
        cc[(u['country'], u['city'], u['region'])].append(u['pk'])
    for c, uu in cc.items():
        city = c[1].strip()
        country = c[0].strip()
        area = c[2].strip()
        kw = {'name__iexact': city, 'country__name__iexact': country, 'area__name__iexact': area}
        if not city:
            print('c', c, City.objects.filter(**kw).count())
            continue
        if not country:
            del kw['country__name__iexact']
        if not area:
            del kw['area__name__iexact']
        n = City.objects.filter(**kw).count()
        if n > 1:
            yield c, n, uu
