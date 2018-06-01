import factory
import factory.fuzzy
from django.conf import settings

from apps.account.models import CustomUser
from . import models


class ProposalFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Proposal

    first_name = factory.Sequence(lambda n: f'first{n:0>6}')
    last_name = factory.Sequence(lambda n: f'last{n:0>6}')
    sex = factory.Iterator([s[0] for s in CustomUser.SEX])
    email = factory.Sequence(lambda n: f'proposal{n:0>6}@domain.mail')
    phone_number = factory.Sequence(lambda n: f'{n:0>12}')
    type = factory.Iterator([t[0] for t in models.Proposal.TYPES])


class HistoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.History

    proposal = factory.SubFactory('apps.proposal.factories.ProposalFactory')
    status = settings.PROPOSAL_OPEN
    reason = models.History.CREATE
