import pytest

from apps.summit.models import SummitAnket
from apps.summit.templatetags.summit_tags import available_summits, is_consultant_for_user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'role,count', [
        (SummitAnket.SUPERVISOR, 1),
        (SummitAnket.CONSULTANT, 1),
        (SummitAnket.VISITOR, 0),
    ], ids=['supervisor', 'consultant', 'visitor'])
def test_available_summits(user, summit_anket_factory, role, count):
    anket = summit_anket_factory(user=user, role=role)

    assert available_summits(user, anket.summit.type).count() == count


@pytest.mark.django_db
class TestIsConsultantForUser:
    @pytest.mark.parametrize(
        'with_user_from', [True, False])
    def test_user_from_dont_have_summit_anket(self, user_factory, summit, with_user_from):
        user_from = user_factory()
        request = type('Request', (), {'user': user_from})
        context = {
            'request': request()
        }
        user_to = user_factory()
        if with_user_from:
            is_consultant = is_consultant_for_user(context, summit, user_to, user_from)
        else:
            is_consultant = is_consultant_for_user(context, summit, user_to)

        assert not is_consultant

    @pytest.mark.parametrize(
        'user_to_have_anket', [True, False], ids=['user_to_with_anket', 'user_to_without_anket'])
    @pytest.mark.parametrize(
        'from_consultant_for_to', [True, False], ids=['user_to_with_anket', 'user_to_without_anket'])
    @pytest.mark.parametrize(
        'with_user_from', [True, False], ids=['with_user_from', 'without_user_from'])
    @pytest.mark.parametrize(
        'role,has_perm',
        [(SummitAnket.SUPERVISOR, True), (SummitAnket.CONSULTANT, True), (SummitAnket.VISITOR, False)],
        ids=['supervisor', 'consultant', 'visitor'])
    def test_user_from_have_anket(
            self, user_factory, summit_anket_factory, summit_user_consultant_factory, summit, role, has_perm,
            with_user_from, user_to_have_anket, from_consultant_for_to):

        anket_from = summit_anket_factory(summit=summit, role=role)
        context_anket = summit_anket_factory(summit=summit, role=role)

        context = {
            'request': type('Request', (), {'user': context_anket.user})()
        }
        user_to = user_factory()
        if user_to_have_anket:
            anket_to = summit_anket_factory(user=user_to, summit=summit)
            if from_consultant_for_to:
                anket = anket_from if with_user_from else context_anket
                summit_user_consultant_factory(consultant=anket, user=anket_to, summit=summit)

        if with_user_from:
            is_consultant = is_consultant_for_user(context, summit, user_to, anket_from.user)
        else:
            is_consultant = is_consultant_for_user(context, summit, user_to)

        assert is_consultant == (user_to_have_anket and from_consultant_for_to and has_perm)
