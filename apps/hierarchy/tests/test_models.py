# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest


@pytest.mark.django_db
class TestHierarchy:
    def test__str__(self, hierarchy):
        assert hierarchy.__str__() == hierarchy.title


@pytest.mark.django_db
class TestDepartment:
    def test__str__(self, department):
        assert department.__str__() == department.title
