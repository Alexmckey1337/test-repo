# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestChurch:
    def test__str__with_title(self, church):
        assert church.__str__() == church.title

    def test__str__without_title(self, church, pastor):
        church.title = ''
        church.save()
        assert church.__str__() == '{} {}'.format(pastor.last_name, church.city)

    def test_get_title_with_title(self, church):
        assert church.get_title == church.title

    def test_get_title_without_title(self, church, pastor):
        church.title = ''
        church.save()
        assert church.get_title == '{} {}'.format(pastor.last_name, church.city)

    def test_get_absolute_url(self, church):
        assert church.get_absolute_url() == reverse('church_detail', args=(church.id,))

    def test_link(self, church):
        assert church.link == reverse('church_detail', args=(church.id,))

    def test_owner_name(self, church, pastor):
        assert church.owner_name == pastor.last_name


@pytest.mark.django_db
class TestHomeGroup:
    def test__str__with_title(self, home_group):
        assert home_group.__str__() == home_group.title

    def test__str__without_title(self, home_group, leader):
        home_group.title = ''
        home_group.save()
        assert home_group.__str__() == '{} {}'.format(leader.last_name, home_group.city)

    def test_get_title_with_title(self, home_group):
        assert home_group.get_title == home_group.title

    def test_get_title_without_title(self, home_group, leader):
        home_group.title = ''
        home_group.save()
        assert home_group.get_title == '{} {}'.format(leader.last_name, home_group.city)

    def test_get_absolute_url(self, home_group):
        assert home_group.get_absolute_url() == reverse('home_group_detail', args=(home_group.id,))

    def test_link(self, home_group):
        assert home_group.link == reverse('home_group_detail', args=(home_group.id,))

    def test_owner_name(self, home_group, leader):
        assert home_group.owner_name == leader.last_name
