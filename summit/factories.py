import datetime
from decimal import Decimal

import factory
import factory.fuzzy

# from payment.factories import CurrencyFactory
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
    start_date = factory.fuzzy.FuzzyDate(start_date=datetime.date(2000, 1, 1))
    end_date = factory.LazyAttribute(lambda o: o.start_date + datetime.timedelta(o.duration))
    full_cost = Decimal('200')
    currency = factory.SubFactory('payment.factories.CurrencyFactory')

    class Params:
        duration = 6


class SummitAnketFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitAnket

    user = factory.SubFactory('account.factories.UserFactory')
    summit = factory.SubFactory(SummitFactory)


class AnketEmailFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AnketEmail

    anket = factory.SubFactory(SummitAnketFactory)
    recipient = 'test@mail.com'
    created_at = factory.LazyFunction(datetime.datetime.now)


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
    owner = factory.SubFactory('account.factories.UserFactory')
    text = factory.fuzzy.FuzzyText(length=51)
    date_created = factory.LazyFunction(datetime.datetime.now)


class SummitAttendFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SummitAttend

    anket = factory.SubFactory(SummitAnketFactory)
    date = factory.LazyFunction(datetime.datetime.now)
