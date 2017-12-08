import factory
import factory.fuzzy

from . import models


class DivisionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Division

    title = factory.Sequence(lambda n: 'Division {}'.format(n))


class StatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Status

    title = factory.Sequence(lambda n: 'Status {}'.format(n))
