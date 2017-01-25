import factory
import factory.fuzzy

from . import models


class NotificationThemeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.NotificationTheme

    title = factory.Sequence(lambda n: 'Notification Theme {}'.format(n))
    description = 'no desc'


class NotificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Notification

    description = 'no desc'

    theme = factory.SubFactory(NotificationThemeFactory)
    user = factory.SubFactory('account.factories.UserFactory')
