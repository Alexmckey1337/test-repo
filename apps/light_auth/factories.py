import factory
import factory.fuzzy

from . import models


class LightAuthUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.LightAuthUser

    user = factory.SubFactory('apps.account.factories.UserFactory')


class PhoneNumberFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PhoneNumber

    auth_user = factory.SubFactory('apps.light_auth.factories.LightAuthUserFactory')
    phone = factory.Sequence(lambda n: f'phone{n:0>6}')


class PhoneConfirmationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PhoneConfirmation

    phone_number = factory.SubFactory('apps.light_auth.factories.PhoneNumberFactory')
    key = factory.Sequence(lambda n: f'{n:0>6}')
