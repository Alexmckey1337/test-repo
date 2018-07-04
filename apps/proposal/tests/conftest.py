import pytest
from pytest_factoryboy import register

from apps.group.factories import DirectionFactory
from apps.location.factories import CityFactory
from apps.proposal.factories import ProposalFactory, HistoryFactory, EventHistoryFactory, EventProposalFactory

register(ProposalFactory)
register(HistoryFactory)
register(EventProposalFactory)
register(EventHistoryFactory)
register(CityFactory)
register(DirectionFactory)


@pytest.fixture
def proposal(proposal_factory):
    return proposal_factory()


@pytest.fixture
def event_proposal(event_proposal_factory):
    return event_proposal_factory()
