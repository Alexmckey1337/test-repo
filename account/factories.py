import factory
import factory.fuzzy

from . import models


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.CustomUser

    username = factory.Sequence(lambda n: 'testuser{}'.format(n))

    first_name = factory.Sequence(lambda n: 'first{}'.format(n))
    last_name = factory.Sequence(lambda n: 'last{}'.format(n))
    middle_name = factory.Sequence(lambda n: 'middle{}'.format(n))

    hierarchy = factory.SubFactory('hierarchy.factories.HierarchyFactory')
