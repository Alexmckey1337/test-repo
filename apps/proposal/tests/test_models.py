import pytest

from apps.proposal.models import History


@pytest.mark.django_db
class TestProposal:
    @pytest.mark.parametrize('first,last,result', [
        ('first', 'last', 'last first'),
        ('', 'last', 'last'),
        ('first', '', 'first'),
        ('', '', 'No Name'),
        (' ', '  ', 'No Name'),
    ], ids=('all', 'only_last', 'only_first', 'empty', 'spaces'))
    def test__str__(self, proposal_factory, first, last, result):
        proposal = proposal_factory(first_name=first, last_name=last)
        assert proposal.__str__() == result

    @pytest.mark.parametrize('lang,expected', [
        (None, {'bbb': 'bbb_ru', 'ccc': 'ccc'}),
        ('ru', {'bbb': 'bbb_ru', 'ccc': 'ccc'}),
        ('de', {'bbb': 'bbb_de', 'ccc': 'ccc'}),
        ('en', {'bbb': 'bbb_en', 'ccc': 'ccc'}),
        ('ja', {'bbb': 'bbb_ru', 'ccc': 'ccc'}),
    ], ids=('default', 'ru', 'de', 'en', 'incorrect'))
    def test_directions_titles(self, proposal_factory, direction_factory, lang, expected):
        direction_factory(code='aaa', title_ru='aaa_ru', title_en='aaa_en', title_de='aaa_de')
        direction_factory(code='bbb', title_ru='bbb_ru', title_en='bbb_en', title_de='bbb_de')
        proposal = proposal_factory(directions=['bbb', 'ccc'])
        if lang is None:
            got = proposal.directions_titles()
        else:
            got = proposal.directions_titles(lang)
        assert got == expected



@pytest.mark.django_db
def test_create_history_record_when_created_proposal(proposal_factory):
    proposal = proposal_factory()

    assert History.objects.filter(proposal=proposal).exists()
