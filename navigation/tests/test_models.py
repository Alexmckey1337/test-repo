# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest


@pytest.mark.django_db
class TestNavigation:
    def test__str__(self, navigation):
        assert navigation.__str__() == 'Test'


@pytest.mark.django_db
class TestCategory:
    def test__str__(self, category):
        assert category.__str__() == category.title


@pytest.mark.django_db
class TestColumnType:
    def test__str__(self, column_type, category):
        assert column_type.__str__() == '{} ({})'.format(column_type.title, category.title)


@pytest.mark.django_db
class TestTable:
    def test__str__(self, table, user):
        assert table.__str__() == user.get_full_name()


@pytest.mark.django_db
class TestColumn:
    def test__str__(self, user_column, column_type):
        assert user_column.__str__() == column_type.title

    def test_editable_true(self, user_column, column_type):
        column_type.editable = True
        column_type.save()
        assert user_column.editable

    def test_editable_false(self, user_column, column_type):
        column_type.editable = False
        column_type.save()
        assert not user_column.editable
