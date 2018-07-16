from django.utils import timezone
from datetime import date
from random import choice, randint, choices

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from apps.account.models import CustomUser, MessengerType, UserMessenger
from apps.group.models import HomeGroup, Church
from apps.hierarchy.models import Hierarchy, Department
from apps.light_auth.models import LightAuthUser, PhoneNumber, PhoneConfirmation
from apps.location.models import City


class Command(BaseCommand):

    def handle(self, *args, **options):
        hierarchies = Hierarchy.objects.all()
        masters = list()

        for i in range(60):
            now = timezone.now()
            ts = int(now.timestamp()*1000)
            master = masters[i%20] if i >= 20 else None
            if master:
                hierarchy = choice(hierarchies.filter(level__lt=master.hierarchy.level))
            else:
                hierarchy = choice(hierarchies.filter(level__gte=2))
            data = dict(
                first_name=f'first{i:0>4}',
                last_name=f'last{i:0>4}',
                middle_name=f'middle{i:0>4}',
                email=f'user{i:0>4}@random.mail',
                spiritual_level=randint(0, 3),
                locality=choice(City.objects.all()[:100]),
                address=f'fakeaddress {randint(111, 444)}',
                phone_number='+380' + str(ts)[4:],
                born_date=date(randint(1944, 2002), randint(1, 12), randint(1, 28)),
                repentance_date=date(randint(2011, 2018), randint(1, 12), randint(1, 28)),
                hierarchy=hierarchy,
                cchurch=(choice(Church.objects.all()) if i % 2 == 0 else None),
                hhome_group=(choice(HomeGroup.objects.all()) if i % 2 == 1 else None),
                language=choice(('ru', 'en', 'de')), sex=choice(('male', 'female')),
                username=f'random{ts:0>14}'
            )
            data['master'] = master
            if i < 20:
                user = CustomUser.add_root(**data)
                masters.append(user)
            else:
                user = master.add_child(**data)
            user.departments.set(choices(Department.objects.all(), k=randint(1, 3)))
            for m in MessengerType.objects.all():
                UserMessenger.objects.create(user=user, messenger=m, value=f'{m.code}{i:0>4}')

            lu = LightAuthUser.objects.create(user=user)
            lu.set_password('password')
            lu.save()
            phone = PhoneNumber.objects.create(auth_user=lu, phone=user.phone_number, verified=True, primary=True)
            key = get_random_string(8).lower()
            while PhoneConfirmation.objects.filter(key=key).exists():
                key = get_random_string(8).lower()
            PhoneConfirmation.objects.create(phone_number=phone, sent=now, key=key)
