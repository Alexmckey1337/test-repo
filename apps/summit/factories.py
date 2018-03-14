from decimal import Decimal
from datetime import date, timedelta

import factory
import factory.fuzzy

# from apps.payment.factories import CurrencyFactory
from django.utils import timezone

from common import date_utils
from . import models


class SummitTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitType

    title = 'Test Summit'
    club_name = 'Team Dream'


class SummitFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Summit

    type = factory.SubFactory(SummitTypeFactory)
    start_date = factory.fuzzy.FuzzyDate(start_date=date(2000, 1, 1))
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(o.duration))
    full_cost = Decimal('200')
    currency = factory.SubFactory('apps.payment.factories.CurrencyFactory')

    class Params:
        duration = 6


class SummitAnketFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitAnket

    user = factory.SubFactory('apps.account.factories.UserFactory')
    summit = factory.SubFactory(SummitFactory)


class AnketEmailFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AnketEmail

    anket = factory.SubFactory(SummitAnketFactory)
    recipient = 'test@mail.com'
    created_at = factory.LazyFunction(timezone.now)


class SummitLessonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitLesson

    summit = factory.SubFactory(SummitFactory)
    name = factory.Sequence(lambda n: 'Lesson #{}'.format(n))


class SummitUserConsultantFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitUserConsultant

    summit = factory.SubFactory(SummitFactory)
    consultant = factory.SubFactory(SummitAnketFactory)
    user = factory.SubFactory(SummitAnketFactory)


class AnketNoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitAnketNote

    summit_anket = factory.SubFactory(SummitAnketFactory)
    owner = factory.SubFactory('apps.account.factories.UserFactory')
    text = factory.fuzzy.FuzzyText(length=51)
    date_created = factory.LazyFunction(timezone.now)


class SummitAttendFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitAttend

    anket = factory.SubFactory(SummitAnketFactory)
    date = factory.LazyFunction(date_utils.today)


class SummitTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitTicket

    title = factory.Sequence(lambda n: 'Ticket #{}'.format(n))
    summit = factory.SubFactory(SummitFactory)


class ProfileStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AnketStatus

    anket = factory.SubFactory(SummitAnketFactory)


class VisitorLocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitVisitorLocation

    visitor = factory.SubFactory(SummitAnketFactory)
    longitude = 11.11
    latitude = 22.22
    date_time = factory.LazyFunction(timezone.now)
