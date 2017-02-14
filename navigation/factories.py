import datetime

import factory
import factory.fuzzy

from . import models


class NavigationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Navigation

    title = 'Test'
    url = '/test/'


class CategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Category

    title = factory.Sequence(lambda n: 'Category #{}'.format(n))
    common = factory.Iterator([True, False])


class ColumnTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ColumnType

    title = factory.Sequence(lambda n: 'column_{}'.format(n))
    category = factory.SubFactory(CategoryFactory)
    verbose_title = factory.Sequence(lambda n: 'Column #{}'.format(n))
    ordering_title = factory.Sequence(lambda n: 'column{}'.format(n))
    number = factory.Sequence(lambda n: n)
    active = True
    editable = True


class TableFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Table

    user = factory.SubFactory('account.factories.UserFactory')


class UserColumnFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Column
        django_get_or_create = ('table', 'columnType')

    table = factory.SubFactory(TableFactory)
    columnType = factory.SubFactory(ColumnTypeFactory)
    number = factory.SelfAttribute('columnType.number')
    active = factory.SelfAttribute('columnType.active')
