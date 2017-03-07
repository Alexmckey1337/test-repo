# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest

from summit.models import SummitAnket


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
