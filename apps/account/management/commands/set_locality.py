from collections import defaultdict

from django.core.management.base import BaseCommand

from apps.group.models import Church, HomeGroup
from apps.location.models import City
from apps.account.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.set_users()
        # self.set_churches()
        # self.set_hg()

    def set_users(self):
        users = CustomUser.objects.filter(locality__isnull=True)
        ucc = defaultdict(list)
        for u in users.values('pk', 'country', 'city', 'region'):
            ucc[(u['country'], u['city'], u['region'])].append(u['pk'])

        not_exist = list()
        multi = list()
        without_country = list()
        without_city = list()
        success = list()
        for cc, uu in ucc.items():
            ok = True
            city = cc[1].strip()
            country = cc[0].strip()
            region = cc[2].strip()
            params = {'name': city, 'country__name': country, 'area__name': region}
            if city == '':
                without_city.append(cc)
                ok = False
            if country == '':
                without_country.append(cc)
                del params['country__name']
            if region == '':
                del params['area__name']
            if not ok:
                continue
            try:
                c = City.objects.get(**params)
            except City.DoesNotExist:
                if region:
                    try:
                        del params['area__name']
                        c = City.objects.get(**params)
                        success.append(cc)
                        CustomUser.objects.filter(pk__in=uu).update(locality=c)
                    except (City.DoesNotExist, City.MultipleObjectsReturned):
                        not_exist.append(cc)
                else:
                    not_exist.append(cc)
            except City.MultipleObjectsReturned:
                multi.append(cc)
            else:
                success.append(cc)
                CustomUser.objects.filter(pk__in=uu).update(locality=c)
        self.stdout.write('USERS')
        self.stdout.write('Without city - %s/%s\n' % (sum([len(ucc[k]) for k in without_city]), len(without_city)))
        self.stdout.write('Without country - %s/%s\n' % (sum([len(ucc[k]) for k in without_country]), len(without_country)))
        self.stdout.write('Not found - %s/%s\n' % (sum([len(ucc[k]) for k in not_exist]), len(not_exist)))
        self.stdout.write('Multi found - %s/%s\n' % (sum([len(ucc[k]) for k in multi]), len(multi)))
        self.stdout.write('Success - %s/%s\n' % (sum([len(ucc[k]) for k in success]), len(success)))

    def set_churches(self):
        churches = Church.objects.all()
        ucc = defaultdict(list)
        for u in churches.values('pk', 'country', 'city'):
            ucc[(u['country'], u['city'])].append(u['pk'])

        not_exist = list()
        multi = list()
        without_country = list()
        without_city = list()
        success = list()
        for cc, uu in ucc.items():
            city = cc[1].strip()
            country = cc[0].strip()
            if city == '' or country == '':
                if city == '':
                    without_city.append(cc)
                if country == '':
                    without_country.append(cc)
                continue
            try:
                c = City.objects.get(name=cc[1], country__name=cc[0])
            except City.DoesNotExist:
                not_exist.append(cc)
            except City.MultipleObjectsReturned:
                multi.append(cc)
            else:
                success.append(cc)
                Church.objects.filter(pk__in=uu).update(locality=c)
        self.stdout.write('CHURCHES')
        self.stdout.write('Without city - %s/%s\n' % (sum([len(ucc[k]) for k in without_city]), len(without_city)))
        self.stdout.write('Without country - %s/%s\n' % (sum([len(ucc[k]) for k in without_country]), len(without_country)))
        self.stdout.write('Not found - %s/%s\n' % (sum([len(ucc[k]) for k in not_exist]), len(not_exist)))
        self.stdout.write('Multi found - %s/%s\n' % (sum([len(ucc[k]) for k in multi]), len(multi)))
        self.stdout.write('Success - %s/%s\n' % (sum([len(ucc[k]) for k in success]), len(success)))

    def set_hg(self):
        hgs = HomeGroup.objects.all()
        ucc = defaultdict(list)
        for u in hgs.values('pk', 'church__country', 'city'):
            ucc[(u['church__country'], u['city'])].append(u['pk'])

        not_exist = list()
        multi = list()
        without_country = list()
        without_city = list()
        success = list()
        for cc, uu in ucc.items():
            city = cc[1].strip()
            country = cc[0].strip()
            if city == '' or country == '':
                if city == '':
                    without_city.append(cc)
                if country == '':
                    without_country.append(cc)
                continue
            try:
                c = City.objects.get(name=cc[1], country__name=cc[0])
            except City.DoesNotExist:
                not_exist.append(cc)
            except City.MultipleObjectsReturned:
                multi.append(cc)
            else:
                success.append(cc)
                HomeGroup.objects.filter(pk__in=uu).update(locality=c)
        self.stdout.write('HG')
        self.stdout.write('Without city - %s/%s\n' % (sum([len(ucc[k]) for k in without_city]), len(without_city)))
        self.stdout.write('Without country - %s/%s\n' % (sum([len(ucc[k]) for k in without_country]), len(without_country)))
        self.stdout.write('Not found - %s/%s\n' % (sum([len(ucc[k]) for k in not_exist]), len(not_exist)))
        self.stdout.write('Multi found - %s/%s\n' % (sum([len(ucc[k]) for k in multi]), len(multi)))
        self.stdout.write('Success - %s/%s\n' % (sum([len(ucc[k]) for k in success]), len(success)))
