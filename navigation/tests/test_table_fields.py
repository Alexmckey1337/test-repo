# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

import pytest

from navigation.models import Category
from navigation.table_fields import group_table, user_table, partner_table, summit_table


@pytest.mark.django_db
@pytest.mark.parametrize('table_name', ('group_table', 'user_table', 'partner_table'))
def test_any_table_when_user_dont_have_table(table, table_name):
    user = table.user
    table.delete()

    module = __import__('navigation.table_fields', {}, {}, [table_name], 0)

    g = getattr(module, table_name)(user)
    assert g == OrderedDict()


@pytest.mark.django_db
@pytest.mark.parametrize('category_title', ('churches', 'home_groups'))
def test_group_table_churches(table, category_title):
    table_columns = group_table(table.user, category_title)
    category = Category.objects.filter(title=category_title)
    assert set(table_columns.keys()) == set(
        category.values_list('columnTypes__title', flat=True))


@pytest.mark.django_db
def test_group_table_group_users(table):
    table_columns = group_table(table.user, 'group_users')
    assert set(table_columns.keys()) < {
        'fullname', 'phone_number', 'repentance_date',
        'spiritual_level', 'born_date'}


@pytest.mark.django_db
def test_group_table_incorrect_category_title(table):
    g = group_table(table.user, 'incorrect')
    assert g == OrderedDict()


@pytest.mark.django_db
def test_user_table(table):
    table_columns = user_table(table.user)
    category = Category.objects.filter(title="Общая информация")
    assert list(table_columns.keys()) == list(
        category.values_list('columnTypes__title', flat=True))


@pytest.mark.django_db
def test_user_table_with_prefix_ordering_title(table):
    table_columns = user_table(table.user, 'some_prefix__')
    assert all(map(lambda a: a['ordering_title'].startswith('some_prefix__'), table_columns.values()))


@pytest.mark.django_db
def test_partner_table(table):
    table_columns = partner_table(table.user)
    category = Category.objects.filter(title="partnership")
    assert list(table_columns.keys()) == [
        field for field in category.values_list('columnTypes__title', flat=True)
        if field not in ('count', 'result_value')]


@pytest.mark.django_db
def test_summit_table(table):
    table_columns = summit_table(table.user)
    category = Category.objects.filter(title="summit")
    assert set(table_columns.keys()) == set(
        category.values_list('columnTypes__title', flat=True))


@pytest.mark.django_db
def test_summit_table_with_prefix_ordering_title(table):
    table_columns = summit_table(table.user, 'some_prefix__')
    assert all(map(lambda a: a['ordering_title'].startswith('some_prefix__'), table_columns.values()))
