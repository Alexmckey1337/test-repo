import pytest
from django.conf import settings

from apps.summit.models import SummitAnket


@pytest.mark.django_db
class TestUser:
    def test__str__(self, user):
        assert user.__str__() == user.fullname

    def test_available_summit_types(self, user, summit_factory, summit_anket_factory, summit_type_factory):
        summit_factory.create_batch(4)
        summit_type_factory.create_batch(2)

        summit_type_consultant = summit_type_factory()
        s = summit_factory(type=summit_type_consultant)
        summit_anket_factory(user=user, summit=s, role=SummitAnket.CONSULTANT)

        summit_type_supervisor = summit_type_factory()
        s = summit_factory(type=summit_type_supervisor)
        summit_anket_factory(user=user, summit=s, role=SummitAnket.SUPERVISOR)

        summit_type_visitor = summit_type_factory()
        s = summit_factory(type=summit_type_visitor)
        summit_anket_factory(user=user, summit=s, role=SummitAnket.VISITOR)

        method_summit_types = list(user.available_summit_types().values_list('id', flat=True))

        assert set(method_summit_types) == {summit_type_consultant.id, summit_type_supervisor.id}
        assert len(method_summit_types) == 2

    @pytest.mark.parametrize('func', ['manager', 'manager_or_high', 'supervisor', 'supervisor_or_high', 'director'])
    def test_is_partner_xxx_user_is_not_partner(self, user, func):
        assert not getattr(user, 'is_partner_{}'.format(func))

    @pytest.mark.parametrize(
        'func,is_true',
        [('manager', False), ('manager_or_high', False),
         ('supervisor', False), ('supervisor_or_high', False),
         ('director', False)])
    def test_is_partner_xxx_user_is_partner(self, user, func, is_true):
        assert getattr(user, 'is_partner_{}'.format(func)) == is_true

    @pytest.mark.parametrize(
        'func,is_true',
        [('manager', True), ('manager_or_high', True),
         ('supervisor', False), ('supervisor_or_high', False),
         ('director', False)])
    def test_is_partner_xxx_user_is_manager(self, user, func, is_true, partner_role_factory):
        partner_role_factory(user=user, level=settings.PARTNER_LEVELS['manager'])
        assert getattr(user, 'is_partner_{}'.format(func)) == is_true

    @pytest.mark.parametrize(
        'func,is_true',
        [('manager', False), ('manager_or_high', True),
         ('supervisor', True), ('supervisor_or_high', True),
         ('director', False)])
    def test_is_partner_xxx_user_is_supervisor(self, user, func, is_true, partner_role_factory):
        partner_role_factory(user=user, level=settings.PARTNER_LEVELS['supervisor'])
        assert getattr(user, 'is_partner_{}'.format(func)) == is_true

    @pytest.mark.parametrize(
        'func,is_true',
        [('manager', False), ('manager_or_high', True),
         ('supervisor', False), ('supervisor_or_high', True),
         ('director', True)])
    def test_is_partner_xxx_user_is_director(self, user, func, is_true, partner_role_factory):
        partner_role_factory(user=user, level=settings.PARTNER_LEVELS['director'])
        assert getattr(user, 'is_partner_{}'.format(func)) == is_true
