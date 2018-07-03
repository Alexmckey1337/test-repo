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

    hierarchy = factory.SubFactory('apps.hierarchy.factories.HierarchyFactory')

    depth = 1
    path = factory.Sequence(lambda n: '%06d' % n)


class UserMessengerFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.UserMessenger

    user = factory.SubFactory('apps.account.factories.UserFactory')
    messenger = factory.SubFactory('apps.account.factories.MessengerTypeFactory')
    value = factory.Sequence(lambda n: f'value{n}')


class MessengerTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.MessengerType

    title = factory.Sequence(lambda n: f'title{n}')
    code = factory.Sequence(lambda n: f'code{n}')
