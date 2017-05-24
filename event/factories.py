# -*- coding: utf-8
from __future__ import unicode_literals

import datetime

import factory
import factory.fuzzy

from account.factories import UserFactory
from . import models


class MeetingTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.MeetingType

    name = factory.Sequence(lambda n: 'Star Wars #{}'.format(n))
    code = factory.Sequence(lambda n: 'star_wars{}'.format(n))


class MeetingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Meeting

    type = factory.SubFactory(MeetingTypeFactory)
    date = factory.fuzzy.FuzzyDate(start_date=datetime.date(2000, 1, 1))
    owner = factory.SubFactory(UserFactory)
    home_group = factory.SubFactory('group.factories.HomeGroupFactory')


class MeetingAttendFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.MeetingAttend

    meeting = factory.SubFactory(MeetingFactory)
    user = factory.SubFactory(UserFactory)
