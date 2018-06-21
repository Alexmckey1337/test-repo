import pytest

from apps.proposal.models import History


@pytest.mark.django_db
class TestProposal:
    @pytest.mark.parametrize('first,last,result', [
        ('first', 'last', 'last first'),
        ('', 'last', 'last'),
        ('first', '', 'first'),
        ('', '', ''),
        (' ', '  ', ''),
    ], ids=('all', 'only_last', 'only_first', 'empty', 'spaces'))
    def test__str__(self, proposal_factory, first, last, result):
        proposal = proposal_factory(first_name=first, last_name=last)
        assert proposal.__str__() == result


@pytest.mark.django_db
def test_create_history_record_when_created_proposal(proposal_factory):
    proposal = proposal_factory()

    assert History.objects.filter(proposal=proposal).exists()
