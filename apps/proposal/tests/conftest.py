import pytest
from pytest_factoryboy import register

from apps.location.factories import CityFactory
from apps.proposal.factories import ProposalFactory, HistoryFactory

register(ProposalFactory)
register(HistoryFactory)
register(CityFactory)


@pytest.fixture
def proposal(proposal_factory):
    return proposal_factory()
