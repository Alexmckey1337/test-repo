import pytest
from pytest_factoryboy import register

from apps.proposal.factories import ProposalFactory, HistoryFactory

register(ProposalFactory)
register(HistoryFactory)


@pytest.fixture
def proposal(proposal_factory):
    return proposal_factory()
