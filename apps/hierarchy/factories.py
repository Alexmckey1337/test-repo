import factory
import factory.fuzzy

from . import models


class DepartmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Department

    title = factory.Sequence(lambda n: f'department{n}')


class HierarchyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Hierarchy

    title = factory.Sequence(lambda n: f'hierarchy{n}')
    level = factory.Sequence(lambda n: n)
    code = factory.Sequence(lambda n: f'mycode{n}')
