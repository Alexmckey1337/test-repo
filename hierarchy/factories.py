import factory
import factory.fuzzy

from . import models


class DepartmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Department

    title = factory.Sequence(lambda n: 'department{}'.format(n))


class HierarchyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Hierarchy

    title = factory.Sequence(lambda n: 'hierarchy{}'.format(n))
    level = factory.Sequence(lambda n: n)
